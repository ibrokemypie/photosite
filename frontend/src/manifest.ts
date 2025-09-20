import { useEffect, useState } from "react";

const BACKEND_URL = Deno.env.get("BACKEND_URL") ?? "http://127.0.0.1/";

const MANIFEST_URL = new URL("manifest.json", BACKEND_URL);

export type ManifestEntry = {
  filename: string;
  created_date: string | undefined;
  keyword_tags: string[];
};

export type Manifest = {
  version: string;
  images: ManifestEntry[];
};

const getManifest = async () => {
  const response = await fetch(MANIFEST_URL);
  const manifestContents = await response.json();

  return manifestContents as Manifest;
};

export const useManifest = () => {
  const [manifest, setManifest] = useState<Manifest | null>(null);

  useEffect(() => {
    const manifestEffect = async () => {
      const manifestContents = await getManifest();
      if (manifestContents) {
        setManifest(manifestContents);
      }
    };
    manifestEffect();
  }, []);

  return manifest;
};
