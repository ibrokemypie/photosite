import { useState } from "react";
import { ManifestEntry, useManifest } from "./manifest.ts";

const BACKEND_URL = Deno.env.get("BACKEND_URL") ?? "http://127.0.0.1/";

type GalleryImageProps = {
  manifestEntry: ManifestEntry;
};

const GalleryImage = (
  { manifestEntry }: GalleryImageProps,
) => {
  const imageCSS = `
	.image {
		display: inline-block;
		overflow: hidden;
	}

	.image > img {
    width: 100%;
	}

  .image > span {
    overflow-wrap: "break-word";
  }
	`;
  return (
    <>
      <style>
        {imageCSS}
      </style>

      <div className="image">
        <img
          src={new URL(manifestEntry.filename, BACKEND_URL).toString()}
        />

        <span>{manifestEntry.created_date}</span>
        <br />
        <span>{manifestEntry.keyword_tags.join(", ")}</span>
      </div>
    </>
  );
};

const galleryCSS = `
  .container {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .innerContainer {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }

	.grid {
		display: grid;

		grid-template-columns: 300px;
		grid-gap: 15px;
	}

	@media only screen and (min-width: 600px) {
		.grid {
		  grid-template-columns: 300px 300px;
		}
	}

	@media only screen and (min-width: 900px) {
		.grid {
		  grid-template-columns: 300px 300px 300px;
		}
	}

  .optionBar {
    padding: 10px 0;
  }
`;

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
      <style>
        {galleryCSS}
      </style>

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
