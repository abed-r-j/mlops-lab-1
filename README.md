# mlops-lab-1

## Question 1

**What do you think the files created by `uv init` contain?**

`uv init` creates the initial structure of the Python project. The main file is `pyproject.toml`, which contains information about the project and its Python dependencies. Other generated files/directories provide the basic project structure and documentation. 

---

## Question 2

**What are the created files? What do you think they are used for? Which ones should be pushed to Git?**

`dvc init` creates the `.dvc` directory and `.dvcignore`. The `.dvc` directory contains DVC configuration and metadata, while `.dvcignore` specifies files that DVC should ignore.

The DVC configuration and metadata that are needed by the project should be pushed to Git. The actual data should not be pushed to Git as normal files; it is managed by DVC. 

---

## Question 3

**Where are the credentials stored? What are the options other than `--global`? Should the credentials be pushed to GitHub?**

When `--global` is used, the DVC remote credentials are stored in the user's global DVC configuration rather than in the project configuration.

Other configuration scopes include local and system-level configuration.

No, the credentials **should not be pushed to GitHub** because they contain authentication information. Only the non-secret configuration should be committed. 

**For our local-remote version of the lab:** no credentials are needed because the DVC remote is a local folder outside the Git repository. 

---

## Question 4

**Take a look at the `.gitignore` file. Explain what happened.**

After running:

```bash
dvc add data
```

DVC adds the `data` directory to `.gitignore`.

This prevents Git from tracking the actual data files. Instead, DVC creates a `data.dvc` pointer file, which Git can track and which identifies the version of the data. 

---

## Question 5

**Do you see a `.dvc` file? What does it contain?**

Yes. After running:

```bash
dvc add data
```

a file called:

```text
data.dvc
```

is created.

It is a **pointer file** for the `data` directory. It contains metadata describing the tracked data, including information used by DVC to identify its particular version. It does not contain the actual dataset. 

---

## Question 6

**On GitHub, is the code there? Is the data there? Do you have any file that points to the data location? What about DagsHub?**

On GitHub, the **code is there** and the DVC pointer file, `data.dvc`, is also there.

The actual dataset is **not stored in GitHub as normal Git files**. `data.dvc` points to/identifies the corresponding DVC-managed data.

After:

```bash
dvc push
```

the actual data is pushed to the configured DVC remote. In the original lab this remote is DagsHub. 

For our modified local setup, the actual data is stored in the **local DVC remote outside the repository** instead of DagsHub. 

---

## Question 7

**In a completely new temporary folder, clone your GitHub repo. Do you see the data folder? What DVC command is needed to get the data folder?**

After cloning the repository, you get the Git-tracked files, including the DVC pointer file, but the actual dataset must be obtained through DVC.

The required command is:

```bash
dvc pull
```

This retrieves the data from the configured DVC remote. 

For our local setup, `dvc pull` retrieves it from the local DVC remote directory.

---

## Question 8

**Do you still see the new folders you created, `food11_processed` and `food11_processed_mini`?**

After checking out an older commit:

```bash
git checkout <old-commit-hash>
```

and then running:

```bash
dvc checkout
```

the working data is changed to match the version described by the older `data.dvc`.

Therefore, **you should no longer see `food11_processed` and `food11_processed_mini`** if those folders were created after the older commit. 

After returning to the main branch:

```bash
git checkout main
dvc checkout
```

the newer data version is restored. 

### Answers in compact form

| Question | Answer                                                                                                                                                   |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1**    | `uv init` creates the initial Python project structure and project configuration such as `pyproject.toml`.                                               |
| **2**    | `dvc init` creates `.dvc` and `.dvcignore`; DVC configuration/metadata are tracked by Git, not the actual dataset.                                       |
| **3**    | `--global` stores credentials/configuration globally. Other scopes include local/system. Credentials must not be pushed to GitHub.                       |
| **4**    | `dvc add data` adds `data` to `.gitignore` so Git does not track the actual dataset.                                                                     |
| **5**    | `data.dvc` is a DVC pointer/metadata file describing the tracked data version.                                                                           |
| **6**    | GitHub contains the code and DVC pointer; the actual data is stored in the DVC remote.                                                                   |
| **7**    | Run `dvc pull` to retrieve the data after cloning.                                                                                                       |
| **8**    | After checking out the older commit and running `dvc checkout`, the newer processed folders should disappear if they did not exist in the older version. |  

---

# mlops-lab-2

## Question 1

After running:

```bash
uv add mlflow torch torchvision scikit-learn
```

`pyproject.toml` is updated to include the newly added dependencies and their version requirements.

`uv.lock` is also updated with the exact resolved dependency versions and dependency information used by the project. This makes the environment reproducible across installations.

Therefore, `pyproject.toml` describes the project's declared dependencies, while `uv.lock` records the resolved versions of those dependencies.

## Question 2

`--backend-store-uri` specifies where MLflow stores its tracking metadata, such as experiments, runs, parameters, metrics, and run information.

In this lab:

```bash
--backend-store-uri sqlite:///mlflow.db
```

means that this metadata is stored in the local SQLite database `mlflow.db`.

`--default-artifact-root` specifies where MLflow stores artifacts produced by runs, such as trained models and other files.

In this lab:

```bash
--default-artifact-root ./mlruns
```

means that the artifacts are stored under the local `mlruns/` directory.

The metadata and artifacts are different: metadata describes the experiment/run and includes parameters and metrics, while artifacts are files generated or saved by the run, such as the trained model.

## Question 3

`mlflow.db` and `mlruns/` should not be tracked by Git because they are generated local MLflow outputs rather than source code.

They should not be tracked by DVC either because they are experiment-tracking outputs, not the Food-11 dataset or another versioned data asset. MLflow itself is responsible for storing and managing them.

The lab therefore adds them to `.gitignore`.

## Question 4

When `mlflow.set_experiment("food11")` is called and an experiment named `food11` does not already exist, MLflow creates that experiment.

After starting the tracking server and calling the function, the new `food11` experiment appears in the MLflow UI alongside the default experiment.

## Question 5

`mlflow.log_param` records a parameter that is set for a run and normally remains fixed for that run, such as learning rate, batch size, number of epochs, or model architecture.

`mlflow.log_metric` records a measured value produced during or after training, such as loss or accuracy.

`log_metric` takes a `step` because the same metric can be recorded multiple times during a run. In this lab, metrics are recorded once per epoch, so `step=epoch` identifies the epoch associated with each value.

A parameter is logged as the configuration of the run, while a metric represents an evolving measurement.

## Question 6

In the MLflow UI, the run page shows the parameters, metric values/charts, and the logged model artifact.

The model artifact is stored on disk under the artifact root configured for the MLflow server:

```text
./mlruns/
```

The exact subdirectory is determined by the MLflow experiment ID and run ID, so the model will be inside the corresponding run's artifact directory rather than directly at `mlruns/model`.

## Question 7

The learning rate that gave the best `val_accuracy` was 0.0001.

Higher learning rate is not always better. A learning rate that is too high can make training unstable or prevent the model from converging well, while a learning rate that is too low can make learning very slow. Therefore, the best value for this experiment is the one associated with the highest observed `val_accuracy`.

## Question 8

The parallel-coordinates plot shows that the runs with (`batch-size`=64 and `lr`=0.001, `batch-size`=32 and `lr`=0.001, `batch-size`=32 and `lr`=0.0001) achieved the higher `val_accuracy`. The experiment does not show that simply increasing `lr` or `batch_size` always improves accuracy; the result depends on the combination of hyperparameters.

## Question 9

The best run according to `val_accuracy` was run a7358eb3206f4a63bac31618759140e8, with a `val_accuracy` of 0.7627737226277372.
