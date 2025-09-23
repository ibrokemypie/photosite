import { Link, useParams } from "react-router";
import { useManifest } from "./manifest.ts";

const BACKEND_URL = Deno.env.get("BACKEND_URL") ?? document.location.toString();

const View = () => {
  const { imageHash } = useParams();
  const manifest = useManifest();

  const manifestEntry = (manifest && imageHash)
    ? manifest.images[imageHash]
    : null;

  const img = manifestEntry
    ? (
      <img
        src={new URL(manifestEntry.filename, BACKEND_URL).toString()}
        style={{ "width": "80%" }}
      />
    )
    : null;

  return (
    <div>
      <Link to="/">{"<"}</Link>
      <br />
      {img}
    </div>
  );
};

export default View;
