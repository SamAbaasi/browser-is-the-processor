let started = false;

self.onmessage = event => {
  if (started) {
    return;
  }

  started = true;

  const {
    file,
    variant
  } = event.data;

  const stdout = [];
  const stderr = [];

  const base =
    "./dist/correctness-v2/" +
    variant +
    "/";

  self.Module = {
    noInitialRun: true,

    locateFile(path) {
      return base + path;
    },

    print(line) {
      stdout.push(String(line));
    },

    printErr(line) {
      stderr.push(String(line));
    },

    onRuntimeInitialized() {
      try {
        if (
          !Module.FS
            .analyzePath("/models")
            .exists
        ) {
          Module.FS.mkdir("/models");
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

        const dumpPath =
          "/tmp/phase6-logits.bin";

        const args = [
          "--model",
          modelPath,

          "--tokens",
          "128000,791,6864,315,9822,374",

          "--threads",
          "1",

          "--ctx",
          "128",

          "--top",
          "10",

          "--dump-logits",
          dumpPath
        ];

        Module.callMain(args);

        const text =
          stdout.join("\n");

        const meta =
          JSON.parse(text);

        const bytes =
          Module.FS.readFile(
            dumpPath
          );

        if (
          bytes.byteLength !==
          meta.n_vocab * 4
        ) {
          throw new Error(
            "logit dump size mismatch: " +
            bytes.byteLength +
            " vs expected " +
            (meta.n_vocab * 4)
          );
        }

        const copy =
          bytes.slice();

        self.postMessage(
          {
            type: "done",
            variant,
            meta,
            stderr,
            logits: copy.buffer
          },
          [copy.buffer]
        );

      } catch (error) {
        self.postMessage({
          type: "error",
          variant,
          stdout,
          stderr,
          message:
            error?.stack ||
            String(error)
        });
      }
    }
  };

  importScripts(
    base +
    "p1-logit-probe.js"
  );
};
