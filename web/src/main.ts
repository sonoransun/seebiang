import { renderGallery } from "./pages/gallery";
import { renderDetail } from "./pages/detail";

const app = document.getElementById("app");
if (!app) throw new Error("missing #app root");

async function route(): Promise<void> {
  const hash = window.location.hash.replace(/^#\/?/, "");
  const match = hash.match(/^variant\/([a-z0-9-]+)$/i);
  if (match) {
    await renderDetail(app!, match[1]);
  } else {
    await renderGallery(app!);
  }
}

window.addEventListener("hashchange", () => {
  void route();
});
void route();
