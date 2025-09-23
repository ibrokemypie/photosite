import { useState } from "react";
import { ManifestEntry, useManifest } from "./manifest.ts";
import { Link } from "react-router";

const BACKEND_URL = Deno.env.get("BACKEND_URL") ?? document.location.toString();

type GalleryImageProps = {
  imageHash: string;
  manifestEntry: ManifestEntry;
};

const GalleryImage = (
  { imageHash, manifestEntry }: GalleryImageProps,
) => {
  return (
    <>
      <div className="image">
        <Link to={{ "pathname": `view/${imageHash}` }}>
          <img
            src={new URL(manifestEntry.thumbnail, BACKEND_URL).toString()}
          />
        </Link>

        <span>{manifestEntry.created_date}</span>
        <br />
        <span>{manifestEntry.keyword_tags.join(", ")}</span>
      </div>
    </>
  );
};

const Gallery = () => {
  const manifest = useManifest();
  const images = manifest?.images ?? {};

  const [isAscending, setIsAscending] = useState(false);

  const sortedImageHashes = Object.keys(images).sort((a, b) => {
    const aValue = images[a].created_date ?? 0;
    const bValue = images[b].created_date ?? 0;

    if (aValue > bValue) {
      if (isAscending) {
        return 1;
      }
      return -1;
    }

    if (aValue < bValue) {
      if (isAscending) {
        return -1;
      }
      return 1;
    }

    return 0;
  });

  const galleryChildren = sortedImageHashes.map((imageHash) => (
    <GalleryImage
      key={imageHash}
      imageHash={imageHash}
      manifestEntry={images[imageHash]}
    />
  ));

  return (
    <>
      <div className="container">
        <div className="innerContainer">
          <div className="optionBar">
            <button
              className="order-button"
              onClick={() => setIsAscending(!isAscending)}
              style={{ transform: isAscending ? undefined : "rotate(180deg)" }}
              type="button"
            >
              ↓
            </button>
          </div>

          <div className="grid">
            {galleryChildren}
          </div>
        </div>
      </div>
    </>
  );
};

export default Gallery;
