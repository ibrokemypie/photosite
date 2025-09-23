import { useState } from "react";
import { ManifestEntry, useManifest } from "./manifest.ts";

const BACKEND_URL = Deno.env.get("BACKEND_URL") ?? document.location.toString();

type GalleryImageProps = {
  manifestEntry: ManifestEntry;
};

const GalleryImage = (
  { manifestEntry }: GalleryImageProps,
) => {
  return (
    <>
      <div className="image">
        <img
          src={new URL(manifestEntry.thumbnail, BACKEND_URL).toString()}
        />

        <span>{manifestEntry.created_date}</span>
        <br />
        <span>{manifestEntry.keyword_tags.join(", ")}</span>
      </div>
    </>
  );
};

const Gallery = () => {
  const manifest = useManifest();

  const [isAscending, setIsAscending] = useState(false);

  const manifestImages = Object.values(manifest?.images ?? {}).sort((a, b) => {
    const aValue = a.created_date ?? 0;
    const bValue = b.created_date ?? 0;

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

  const galleryChildren = manifestImages.map((entry) => (
    <GalleryImage
      key={entry.filename}
      manifestEntry={entry}
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
