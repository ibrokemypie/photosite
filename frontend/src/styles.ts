// @ts-expect-error - don't complain about importing css
import styles from "./styles.css"; // with { type: "css" }; need deno bundle to
// update esbuild version to 0.19.7
// https://github.com/evanw/esbuild/issues/3384#issuecomment-2090206186
export { styles };
