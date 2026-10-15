# Run from the coordinator checkout; inspect and commit the study changes separately.
git -C studies/narps config -f .gitmodules submodule.results/preparation-e2e-worker-20261015.path results/preparation-e2e-worker-20261015
git -C studies/narps config -f .gitmodules submodule.results/preparation-e2e-worker-20261015.url git@github.com:leej3/stamped-ai-research-next.git
git -C studies/narps update-index --add --cacheinfo 160000,4daf37c70dca92b981861b05794696afe0dbfad7,results/preparation-e2e-worker-20261015
git -C studies/narps add .gitmodules
