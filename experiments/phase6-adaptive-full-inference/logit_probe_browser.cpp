#include "llama.h"

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <fstream>
#include <iostream>
#include <limits>
#include <sstream>
#include <string>
#include <vector>

static std::vector<llama_token> parse_tokens(const std::string & s) {
    std::vector<llama_token> out;

    if (s.empty()) {
        return out;
    }

    std::stringstream ss(s);
    std::string item;

    while (std::getline(ss, item, ',')) {
        out.push_back((llama_token) std::stoi(item));
    }

    return out;
}

static std::vector<int> parse_ints(const std::string & s) {
    std::vector<int> out;

    if (s.empty()) {
        return out;
    }

    std::stringstream ss(s);
    std::string item;

    while (std::getline(ss, item, ',')) {
        out.push_back(std::stoi(item));
    }

    return out;
}

int main(int argc, char ** argv) {
    std::string model_path;
    std::string input_csv;
    std::string force_csv;
    std::string candidates_csv;
    std::string dump_logits_path;

    int threads = 1;
    int n_ctx = 128;
    int top_n = 10;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];

        if (arg == "--model" && i + 1 < argc) {
            model_path = argv[++i];
        } else if (arg == "--tokens" && i + 1 < argc) {
            input_csv = argv[++i];
        } else if (arg == "--force" && i + 1 < argc) {
            force_csv = argv[++i];
        } else if (arg == "--candidates" && i + 1 < argc) {
            candidates_csv = argv[++i];
        } else if (arg == "--dump-logits" && i + 1 < argc) {
            dump_logits_path = argv[++i];
        } else if (arg == "--threads" && i + 1 < argc) {
            threads = std::stoi(argv[++i]);
        } else if (arg == "--ctx" && i + 1 < argc) {
            n_ctx = std::stoi(argv[++i]);
        } else if (arg == "--top" && i + 1 < argc) {
            top_n = std::stoi(argv[++i]);
        } else {
            std::cerr << "Unknown/incomplete argument: " << arg << "\n";
            return 2;
        }
    }

    if (model_path.empty() || input_csv.empty()) {
        std::cerr
            << "usage: p1-logit-probe "
            << "--model MODEL "
            << "--tokens IDS "
            << "[--force IDS] "
            << "[--candidates IDS] "
            << "[--threads N] "
            << "[--ctx N] "
            << "[--top N]\n";
        return 2;
    }

    auto input = parse_tokens(input_csv);
    auto forced = parse_tokens(force_csv);
    auto candidates = parse_ints(candidates_csv);

    llama_backend_init();

    llama_model_params model_params =
        llama_model_default_params();

    model_params.n_gpu_layers = 0;
    model_params.use_mmap = false;

    llama_model * model =
        llama_load_model_from_file(
            model_path.c_str(),
            model_params
        );

    if (!model) {
        std::cerr << "failed to load model\n";
        llama_backend_free();
        return 1;
    }

    llama_context_params ctx_params =
        llama_context_default_params();

    ctx_params.n_ctx = n_ctx;
    ctx_params.n_batch =
        std::max<int>(1, (int) input.size());
    ctx_params.n_threads = threads;
    ctx_params.n_threads_batch = threads;

    llama_context * ctx =
        llama_new_context_with_model(
            model,
            ctx_params
        );

    if (!ctx) {
        std::cerr << "failed to create context\n";
        llama_free_model(model);
        llama_backend_free();
        return 1;
    }

    // Same schedule as oracle:
    // initial prompt is one batch.
    llama_batch batch =
        llama_batch_get_one(
            input.data(),
            (int32_t) input.size(),
            0,
            0
        );

    if (llama_decode(ctx, batch) != 0) {
        std::cerr << "initial decode failed\n";
        return 1;
    }

    // Then replay already-generated tokens one at a time.
    llama_pos next_pos = (llama_pos) input.size();

    for (llama_token token : forced) {
        llama_token one = token;

        llama_batch next =
            llama_batch_get_one(
                &one,
                1,
                next_pos,
                0
            );

        if (llama_decode(ctx, next) != 0) {
            std::cerr << "forced decode failed\n";
            return 1;
        }

        ++next_pos;
    }

    float * logits = llama_get_logits(ctx);
    const int32_t n_vocab = llama_n_vocab(model);

    if (!logits || n_vocab <= 0) {
        std::cerr << "invalid logits\n";
        return 1;
    }

    if (!dump_logits_path.empty()) {
        std::ofstream out(
            dump_logits_path,
            std::ios::binary
        );

        if (!out) {
            std::cerr << "failed to open logit dump\n";
            return 1;
        }

        out.write(
            reinterpret_cast<const char *>(logits),
            (std::streamsize) n_vocab * sizeof(float)
        );

        if (!out) {
            std::cerr << "failed to write logit dump\n";
            return 1;
        }
    }

    std::vector<int> ids(n_vocab);

    for (int i = 0; i < n_vocab; ++i) {
        ids[i] = i;
    }

    auto score = [&](int id) {
        const float v = logits[id];

        return std::isnan(v)
            ? -std::numeric_limits<float>::infinity()
            : v;
    };

    const int take = std::min(top_n, n_vocab);

    std::partial_sort(
        ids.begin(),
        ids.begin() + take,
        ids.end(),
        [&](int a, int b) {
            return score(a) > score(b);
        }
    );

    int nan_count = 0;
    int inf_count = 0;

    double sum = 0.0;
    double sum_sq = 0.0;

    float min_logit =
        std::numeric_limits<float>::infinity();

    float max_logit =
        -std::numeric_limits<float>::infinity();

    for (int i = 0; i < n_vocab; ++i) {
        const float v = logits[i];

        if (std::isnan(v)) {
            ++nan_count;
            continue;
        }

        if (!std::isfinite(v)) {
            ++inf_count;
            continue;
        }

        min_logit = std::min(min_logit, v);
        max_logit = std::max(max_logit, v);

        sum += (double) v;
        sum_sq += (double) v * (double) v;
    }

    std::cout << std::setprecision(9);

    std::cout << "{\n";
    std::cout << "  \"n_ctx\": " << n_ctx << ",\n";
    std::cout << "  \"n_vocab\": " << n_vocab << ",\n";
    std::cout << "  \"input_count\": " << input.size() << ",\n";
    std::cout << "  \"forced_count\": " << forced.size() << ",\n";
    std::cout << "  \"nan_count\": " << nan_count << ",\n";
    std::cout << "  \"inf_count\": " << inf_count << ",\n";
    std::cout << "  \"min_logit\": " << min_logit << ",\n";
    std::cout << "  \"max_logit\": " << max_logit << ",\n";
    std::cout << "  \"sum\": " << sum << ",\n";
    std::cout << "  \"l2_squared\": " << sum_sq << ",\n";

    std::cout << "  \"top\": [\n";

    for (int i = 0; i < take; ++i) {
        const int id = ids[i];

        std::cout
            << "    {\"token\": "
            << id
            << ", \"logit\": "
            << logits[id]
            << "}";

        if (i + 1 != take) {
            std::cout << ",";
        }

        std::cout << "\n";
    }

    std::cout << "  ],\n";

    std::cout << "  \"candidates\": [\n";

    for (size_t i = 0; i < candidates.size(); ++i) {
        const int id = candidates[i];

        std::cout
            << "    {\"token\": "
            << id
            << ", \"logit\": "
            << logits[id]
            << "}";

        if (i + 1 != candidates.size()) {
            std::cout << ",";
        }

        std::cout << "\n";
    }

    std::cout << "  ]\n";
    std::cout << "}\n";

    llama_free(ctx);
    llama_free_model(model);
    llama_backend_free();

    return 0;
}
