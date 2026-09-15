# mlops-lab-1

## Question 1

`uv init` creates the initial Python project structure. The main file is `pyproject.toml`, which contains project metadata, Python requirements, dependencies, and build configuration. `.python-version` specifies the Python version used by the project. The `src` directory contains the Python source code and `README.md` contains project documentation. Additional files such as `.venv` and `uv.lock` can be created later when the project environment and dependencies are used.

## Question 2

`dvc init` creates the `.dvc` directory and `.dvcignore`. The `.dvc` directory contains DVC configuration and metadata needed to manage the project's data. `.dvcignore` tells DVC which files to ignore. The non-secret DVC configuration and metadata needed for reproducing the project should be committed to Git, while credentials and other secrets should not be pushed to GitHub.

## Question 3

When `--global` is used, DVC stores the remote configuration in the user's global DVC configuration instead of the project's `.dvc/config`. Other configuration scopes include local and system-level configuration. DagsHub credentials are secrets and should not be pushed to GitHub. Only non-sensitive DVC configuration should be committed.

## Question 4

After running `dvc add data`, DVC adds the `data` directory to `.gitignore`. This prevents Git from tracking the actual dataset files. Instead, DVC creates a pointer file that describes the version of the tracked data.

## Question 5

Yes, a `data.dvc` file is created. It contains DVC metadata describing the `data` directory, including a content hash that identifies the version of the dataset. It does not contain the actual images.

## Question 6

GitHub contains the project source code and DVC pointer/configuration files such as `data.dvc`, but the actual Food-11 image dataset is not stored there as normal Git files. The `data.dvc` file identifies the corresponding data version. After running `dvc push`, the actual dataset is uploaded to the DVC remote on DagsHub.

## Question 7

After cloning the GitHub repository into a new temporary folder, the Git-tracked files and DVC pointer files are available, but the actual dataset is not obtained through Git. The required command to download the data from the DVC remote is:

```bash
dvc pull
```

## Question 8

After checking out an older Git commit, the `data.dvc` pointer is changed to the older version. Running `dvc checkout` synchronizes the working data with that version. Therefore, the newer `food11_processed` and `food11_processed_mini` folders should no longer be present if they were added only in the newer data version. Returning to `main` and running `dvc checkout` restores the latest data version.
