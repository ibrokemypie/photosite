// this file contains bundling logic.
// why am I not using `deno bundle`?
// because I haven't yet found a good way to get runtime configuration into the
// output, so I am using this to allow Deno.env.get() calls in runtime code which
// will be rewritten to their result at bundle time.

const args = Deno.args;

const writeBundle = async () => {
  // @ts-expect-error: for some reason bundle isn't a property of the Deno type
  // even in Deno 2.5, so I have to do this for now.
  const result = await Deno.bundle({
    entrypoints: ["src/index.html"],
    outputDir: "dist",
    platform: "browser",
    minify: args.includes("--minify"),
    write: false,
  });

  try {
    await Deno.mkdir("dist");
  } catch (e) {
    if (!(e instanceof Deno.errors.AlreadyExists)) {
      throw e;
    }
  }

  for (const file of result.outputFiles!) {
    const parsedBundle = file.text().replace(
      /Deno\.env\.get\("([^"]*)"\)/g,
      (_: string, key: string) => {
        const value = Deno.env.get(key);
        if (value) {
          return `"${value}"`;
        }
      },
    );

    await Deno.writeTextFile(file.path, parsedBundle);
    console.log("Wrote file", file.path);
  }
};

writeBundle();

if (args.includes("--watch")) {
  const watcher = Deno.watchFs("src");
  for await (const _ of watcher) {
    try {
      await writeBundle();
    } catch (e) {
      console.log(e);
    }
  }
}
