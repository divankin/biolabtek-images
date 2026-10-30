# BioLabTek cover photos

Prepares the cover photo for each product imported from Machinio into the BioLabTek Shopify store.

For every cover listed in `covers.json`, the workflow in `.github/workflows/process.yml`:

1. downloads the original photo into `originals/`
2. removes the background (rembg, BiRefNet model), places the instrument on white, and adds the BioLabTek logo centered at 25% opacity, saved in `cutout/`
3. saves the original photo with the same watermark in `watermark/`, used when a cutout doesn't look right
4. builds before/after review sheets in `sheets/`

Shopify copies each photo when the products are imported, so this repo is only needed until the import is done.
