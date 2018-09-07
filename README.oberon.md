# Notes on the phonemizer's "master-oberon" branch

* This branch is devoted to the testing and deployment of *phonemizer*
  on the CoML cluster (called oberon).

* Simply do a merge request from `master` to `master-oberon`.

* The merge will trigger the build/test/deployment of phonemizer on
  oberon (as defined in the `.gitlab-ci.yml` file).

* Once deployed, the new version is available for the users on obeon
  with:

        module load python-anaconda
        source activate wordseg

  Note the phonemizer is installed on the *wordseg* virtual environment.
