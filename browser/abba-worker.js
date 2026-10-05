importScripts("./frozen-workload.js");

function csv(xs) {
  return xs.join(",");
}

let started = false;

self.onmessage = event => {
  if (started) {
    return;
  }

  started = true;

  const {
    file,
    variant,
    kind,
    nTokens,
    runIndex
  } = event.data;

  const records = [];

  const script =
    "./dist/" +
    variant +
    "/p1-browser-workload-bench.js";

  self.Module = {
    noInitialRun: true,

    locateFile(path) {
      return (
        "./dist/" +
        variant +
        "/" +
        path
      );
    },

    print(line) {
      const text = String(line);

      try {
        const parsed =
          JSON.parse(text);

        records.push(parsed);

        self.postMessage({
          type: "record",
          runIndex,
          variant,
          record: parsed
        });

      } catch {
        self.postMessage({
          type: "stdout",
          runIndex,
          variant,
          line: text
        });
      }
    },

    printErr(line) {
      self.postMessage({
        type: "stderr",
        runIndex,
        variant,
        line: String(line)
      });
    },

    onRuntimeInitialized() {
      try {
        if (
          !Module.FS
            .analyzePath("/models")
            .exists
        ) {
          Module.FS.mkdir(
            "/models"
          );
        }

        Module.FS.mount(
          Module.WORKERFS,
          {
            files: [file]
          },
          "/models"
        );

        const modelPath =
          "/models/" +
          file.name;

        const w =
          self.P1_WORKLOAD;

        const args = [
          "--model",
          modelPath,

          "--kind",
          kind,

          "--tokens",
          String(nTokens),

          "--seed-tokens",
          csv(w.seed),

          "--decode-input",
          csv(w.decode_input),

          "--decode-force",
          csv(w.decode_force),

          "--repeats",
          "3"
        ];

        const workerStart =
          performance.now();

        Module.callMain(args);

        const workerEnd =
          performance.now();

        self.postMessage({
          type: "done",
          runIndex,
          variant,
          kind,
          nTokens,
          records,
          workerWallMs:
            workerEnd -
            workerStart
        });

      } catch (error) {
        self.postMessage({
          type: "error",
          runIndex,
          variant,
          message:
            error?.stack ||
            String(error)
        });
      }
    }
  };

  importScripts(script);
};
