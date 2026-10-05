importScripts(
  "./dist/triple-v6/p1-triple-v6.js?v=phase5d1"
);

const WASM_SHA256 =
  "944fc9f7818d34383a012328525243b069bf77fd147aa4ce22a08f657b720561";

const NS = [
  2560,
  3200,
  6912,
  8192
];

const VARIANTS = [
  "generic",
  "dot",
  "pairwise"
];

const TUNE_N = 6912;

const CONFIDENCE_THRESHOLD = 0.05;

const SOFT_CONFIRMATION_DEADLINE_MS = 140;

const PREWARM_TARGET_MS = 3;
const PREWARM_INTERNAL_ROUNDS = 1;

const STAGE1_TARGET_MS = 4;
const STAGE1_INTERNAL_ROUNDS = 1;

const CONFIRM_TARGET_MS = 4;
const CONFIRM_INTERNAL_ROUNDS = 1;

const STAGE1_ORDERS = [
  ["generic", "dot", "pairwise"],
  ["dot", "pairwise", "generic"],
  ["pairwise", "generic", "dot"]
];

let modulePromise = null;


function median(xs) {
  const a = [...xs].sort(
    (x, y) => x - y
  );

  const mid =
    Math.floor(a.length / 2);

  if (a.length % 2) {
    return a[mid];
  }

  return (
    a[mid - 1] +
    a[mid]
  ) / 2;
}


function functionForVariant(
  variant
) {
  if (variant === "generic") {
    return "p1_measure_generic_ms";
  }

  if (variant === "dot") {
    return "p1_measure_dot_ms";
  }

  if (variant === "pairwise") {
    return "p1_measure_pairwise_ms";
  }

  throw new Error(
    `Unknown variant: ${variant}`
  );
}


function measure(
  module,
  variant,
  n,
  targetMs,
  rounds
) {
  return module.ccall(
    functionForVariant(variant),
    "number",
    [
      "number",
      "number",
      "number"
    ],
    [
      n,
      targetMs,
      rounds
    ]
  );
}


function verify(
  module,
  n
) {
  return module.ccall(
    "p1_verify",
    "number",
    ["number"],
    [n]
  );
}


function buildScores(
  samples
) {
  const scores = {};

  for (
    const variant of VARIANTS
  ) {
    const xs =
      samples[variant];

    scores[variant] = {
      samples_ms:
        [...xs],

      sample_count:
        xs.length,

      median_ms:
        median(xs)
    };
  }

  return scores;
}


function rankScores(
  scores
) {
  return [...VARIANTS].sort(
    (a, b) =>
      scores[a].median_ms -
      scores[b].median_ms
  );
}


function margin(
  scores,
  ranking
) {
  return (
    scores[
      ranking[1]
    ].median_ms /
    scores[
      ranking[0]
    ].median_ms
  ) - 1;
}


function progress(
  message
) {
  self.postMessage({
    type: "progress",
    message
  });
}


async function getModule() {
  if (!modulePromise) {
    modulePromise =
      createP1TripleV6({
        locateFile(path, prefix) {
          if (
            path.endsWith(".wasm")
          ) {
            return (
              "./dist/triple-v6/" +
              "p1-triple-v6.wasm" +
              "?v=phase5d1"
            );
          }

          return prefix + path;
        },

        print() {},
        printErr() {}
      });
  }

  return modulePromise;
}


async function runSelector() {
  const suiteStarted =
    performance.now();

  progress(
    "Loading frozen Phase 4D WASM..."
  );

  const module =
    await getModule();

  //
  // Correctness verification is outside selector wall.
  //
  const verifyStarted =
    performance.now();

  for (const n of NS) {
    const mask =
      verify(module, n);

    if (mask !== 7) {
      throw new Error(
        `Verification failed at n=${n}, mask=${mask}`
      );
    }
  }

  const verificationWallMs =
    performance.now() -
    verifyStarted;

  progress(
    "Correctness verification PASS."
  );

  //
  // Selector timing begins before prewarm.
  //
  const selectorStarted =
    performance.now();

  for (
    const variant of VARIANTS
  ) {
    measure(
      module,
      variant,
      TUNE_N,
      PREWARM_TARGET_MS,
      PREWARM_INTERNAL_ROUNDS
    );
  }

  const samples = {
    generic: [],
    dot: [],
    pairwise: []
  };

  progress(
    "Running Stage 1..."
  );

  for (
    let cycle = 0;
    cycle < STAGE1_ORDERS.length;
    ++cycle
  ) {
    const order =
      STAGE1_ORDERS[cycle];

    for (
      let position = 0;
      position < order.length;
      ++position
    ) {
      const variant =
        order[position];

      const value =
        measure(
          module,
          variant,
          TUNE_N,
          STAGE1_TARGET_MS,
          STAGE1_INTERNAL_ROUNDS
        );

      samples[
        variant
      ].push(value);

      self.postMessage({
        type: "sample",

        stage: 1,

        cycle:
          cycle + 1,

        position:
          position + 1,

        variant,

        ms_per_call:
          value
      });
    }
  }

  const stage1Scores =
    buildScores(samples);

  const stage1Ranking =
    rankScores(stage1Scores);

  const stage1Margin =
    margin(
      stage1Scores,
      stage1Ranking
    );

  const elapsedAfterStage1 =
    performance.now() -
    selectorStarted;

  let confirmationTriggered =
    false;

  let confirmationSkippedForBudget =
    false;

  let confirmationOrder =
    null;

  let elapsedBeforeConfirmation =
    null;

  if (
    stage1Margin <
    CONFIDENCE_THRESHOLD
  ) {
    elapsedBeforeConfirmation =
      performance.now() -
      selectorStarted;

    if (
      elapsedBeforeConfirmation <
      SOFT_CONFIRMATION_DEADLINE_MS
    ) {
      confirmationTriggered =
        true;

      const best =
        stage1Ranking[0];

      const second =
        stage1Ranking[1];

      confirmationOrder = [
        best,
        second
      ];

      progress(
        `Near tie ${(stage1Margin * 100).toFixed(2)}%; ` +
        `running one confirmation pair.`
      );

      for (
        let position = 0;
        position < confirmationOrder.length;
        ++position
      ) {
        const variant =
          confirmationOrder[
            position
          ];

        const value =
          measure(
            module,
            variant,
            TUNE_N,
            CONFIRM_TARGET_MS,
            CONFIRM_INTERNAL_ROUNDS
          );

        samples[
          variant
        ].push(value);

        self.postMessage({
          type: "sample",

          stage: 2,

          cycle: 1,

          position:
            position + 1,

          variant,

          ms_per_call:
            value
        });
      }
    }
    else {
      confirmationSkippedForBudget =
        true;

      progress(
        "Near tie detected, but confirmation skipped because soft deadline was reached."
      );
    }
  }

  const finalScores =
    buildScores(samples);

  const finalRanking =
    rankScores(finalScores);

  const finalMargin =
    margin(
      finalScores,
      finalRanking
    );

  const selectedVariant =
    finalRanking[0];

  let decisionMode;

  if (
    stage1Margin >=
    CONFIDENCE_THRESHOLD
  ) {
    decisionMode =
      "clear-winner-stage1";
  }
  else if (
    confirmationTriggered
  ) {
    decisionMode =
      "bounded-confirmation-pair";
  }
  else {
    decisionMode =
      "near-tie-stage1-budget-stop";
  }

  const bestMedian =
    finalScores[
      finalRanking[0]
    ].median_ms;

  const equivalenceSet =
    VARIANTS.filter(
      variant =>
        finalScores[
          variant
        ].median_ms <=
        bestMedian *
        (
          1 +
          CONFIDENCE_THRESHOLD
        )
    );

  const selectorWallMs =
    performance.now() -
    selectorStarted;

  const result = {
    schema:
      "p1-phase5d-autotune-v1",

    timestamp:
      new Date().toISOString(),

    browser:
      self.navigator.userAgent,

    hardware_concurrency:
      self.navigator.hardwareConcurrency ??
      null,

    device_memory_gb:
      self.navigator.deviceMemory ??
      null,

    cross_origin_isolated:
      self.crossOriginIsolated,

    frozen_wasm_sha256:
      WASM_SHA256,

    protocol: {
      tune_n:
        TUNE_N,

      confidence_threshold:
        CONFIDENCE_THRESHOLD,

      soft_confirmation_deadline_ms:
        SOFT_CONFIRMATION_DEADLINE_MS,

      prewarm_target_ms:
        PREWARM_TARGET_MS,

      prewarm_internal_rounds:
        PREWARM_INTERNAL_ROUNDS,

      stage1_target_ms:
        STAGE1_TARGET_MS,

      stage1_internal_rounds:
        STAGE1_INTERNAL_ROUNDS,

      stage1_orders:
        STAGE1_ORDERS,

      confirmation_target_ms:
        CONFIRM_TARGET_MS,

      confirmation_internal_rounds:
        CONFIRM_INTERNAL_ROUNDS,

      max_confirmation_pairs:
        1,

      selector_gate_ms:
        200,

      canonical_regret_gate:
        1.02,

      canonical_oracle:
        "Phase 4D frozen cross-platform v6.2",

      live_validation:
        false
    },

    selector: {
      stage1_scores:
        stage1Scores,

      stage1_ranking:
        stage1Ranking,

      stage1_margin:
        stage1Margin,

      elapsed_after_stage1_ms:
        elapsedAfterStage1,

      confirmation_triggered:
        confirmationTriggered,

      extension_triggered:
        confirmationTriggered,

      confirmation_skipped_for_budget:
        confirmationSkippedForBudget,

      confirmation_order:
        confirmationOrder,

      extension_top_two:
        confirmationOrder,

      elapsed_before_confirmation_ms:
        elapsedBeforeConfirmation,

      final_scores:
        finalScores,

      final_ranking:
        finalRanking,

      final_margin:
        finalMargin,

      equivalence_set:
        equivalenceSet,

      decision_mode:
        decisionMode,

      selected_variant:
        selectedVariant,

      selector_wall_ms:
        selectorWallMs,

      passes_wall_time_gate:
        selectorWallMs < 200
    },

    gates: {
      selector_wall_under_200ms:
        selectorWallMs < 200
    },

    verification_wall_ms:
      verificationWallMs,

    suite_wall_ms:
      performance.now() -
      suiteStarted
  };

  return result;
}


self.onmessage =
  async event => {

    if (
      !event.data ||
      event.data.type !== "run"
    ) {
      return;
    }

    try {
      const result =
        await runSelector();

      self.postMessage({
        type: "result",
        result
      });
    }
    catch (error) {
      self.postMessage({
        type: "error",

        message:
          error?.stack ||
          error?.message ||
          String(error)
      });
    }
  };
