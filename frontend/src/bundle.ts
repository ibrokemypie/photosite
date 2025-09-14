// this file contains bundling logic.
// why am I not using `deno bundle`?
// because I haven't yet found a good way to get runtime configuration into the
// output, so I am using this to allow Deno.env.get() calls in runtime code which
// will be rewritten to their result at bundle time.

const writeBundle = async () => {
  // @ts-expect-error: for some reason bundle isn't a property of the Deno type
  // even in Deno 2.5, so I have to do this for now.
  const result = await Deno.bundle({
    entrypoints: ["src/index.html"],
    outputDir: "dist",
    platform: "browser",
    minify: false,
    write: false,
  });

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

const args = Deno.args;

if (args.includes("--watch")) {
  const watcher = Deno.watchFs("src");
  for await (const _ of watcher) {
    await writeBundle();
  }
}
