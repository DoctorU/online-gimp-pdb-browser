# Script-Fu Index

A GitHub Pages browser for GIMP's built-in Script-Fu procedures. It indexes procedure names,
summaries, menu locations, authorship, supported image/drawable types, and selectable parameters
from the Scheme scripts in GIMP's source repository.

## Run locally

```sh
git clone --depth 1 https://github.com/GNOME/gimp.git /tmp/gimp
python3 scripts/build_pdb.py \
	--source-dir /tmp/gimp/plug-ins/script-fu/scripts \
	--pdb-c-dir /tmp/gimp/app/pdb \
	--revision "$(git -C /tmp/gimp rev-parse HEAD)"
python3 -m http.server 8000
```

Open `http://localhost:8000`. The site itself is static; its catalog is generated into `data/pdb.json`.

## Rebuild and publish

The `Build and deploy Script-Fu Index` workflow fetches the latest GIMP source, rebuilds the catalog,
and publishes the site to GitHub Pages. It runs daily at 06:23 UTC, on pushes to `main`, when started
manually from the Actions tab, and when a tag matching `rebuild-pdb-*` is pushed. The generated
source links point to the exact GIMP commit used for that deployment.

Enable GitHub Pages for the repository with **GitHub Actions** as its build and deployment source.

## License

The project is licensed under the GNU General Public License, version 3 or (at your option) any later
version (GPL-3.0-or-later), matching GIMP's source license. See [LICENSE](LICENSE).
