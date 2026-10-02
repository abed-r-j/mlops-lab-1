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

---

# mlops-lab-3

## Question 1

The model was registered under the name **`food11`** and was given **version 4**. Version 4 is currently assigned the **`champion`** alias and was produced by run `56e852327df34614a957136ef8b51913`.

A **run's logged model artifact** is the trained model saved as an artifact belonging to a specific MLflow run. It is tied to that experiment run and its recorded parameters and metrics. A **registered model** is a separate Model Registry entity with a shared name (`food11`) that can contain multiple model versions, each associated with a run. This allows models to be managed and deployed independently of the individual training runs.

## Question 2

The old built-in MLflow stages such as `Staging` and `Production` have been replaced by model aliases such as `champion` and `challenger`.

A model is versioned separately from the run that produced it because multiple runs can produce different versions of the same logical model. The Registry provides a stable model name and version history independently of individual experiment runs.

An alias is more flexible than a fixed stage because an alias is a mutable pointer. For example, `champion` can point to version 1 today and be reassigned to version 2 later without changing either model version. This allows the serving application to continue using `models:/food11@champion` while the alias is moved to a newer version.

## Question 3

Using `models:/food11@champion` allows the serving application to obtain whichever model version is currently assigned the `champion` alias. This separates the serving code from a specific file location and allows the model to be managed through the MLflow Model Registry.

If a newer model version is registered and should be served, the serving code does not need to change. The `champion` alias can simply be reassigned to the newer version in the Model Registry.

## Question 4

`pyproject.toml` and `uv.lock` are copied before the source code so that Docker can cache the dependency-installation layer. If only `serve.py` changes, the dependency files have not changed, so Docker can reuse the cached dependency layer and only rebuild the layers after the source code is copied.

If all source files were copied before installing dependencies, a small source-code change could invalidate the dependency layer and cause the dependencies to be installed again, making rebuilds slower.

## Question 5

The measured size of the **multi-stage Docker image** (`food11-api:latest`) is **3,104,053,887 bytes**, while the **naive single-stage image** (`food11-api:naive`) is **3,139,344,207 bytes**.

Therefore, the multi-stage image is **35,290,320 bytes smaller**, which is approximately **33.7 MiB** or about **1.12% smaller** than the naive image.

From `docker history`, the largest layer in the multi-stage image is the copied `.venv` at approximately **5.81 GB**, while the naive image has a **5.86 GB** layer created by `uv sync`. This shows that the Python environment and its dependencies dominate the image size. The multi-stage build still produces a smaller final image because the builder-stage tooling and intermediate layers are not included in the runtime image.

## Question 6

If `.dockerignore` is missing, Docker sends many unnecessary files from the project directory to the Docker daemon as the build context. This increases the amount of data transferred and can make builds slower.

It can also make the image build process unnecessarily large because files that are not needed by the application become available to the build.

For this lab, folders such as `.venv/`, `data/`, `mlruns/`, `mlflow.db`, `.git/`, and `__pycache__/` should be excluded because the Docker image does not need them. None of these folders is required by the Dockerfile described in the lab; the important runtime inputs are the dependencies and `src/`.

## Question 7

`127.0.0.1` inside a container refers to the container itself, not the Windows host machine. Therefore, `127.0.0.1:5000` inside the container does not refer to the MLflow server running on the host.

On Docker Desktop for Windows and Mac, `host.docker.internal` provides a hostname that allows a container to reach services running on the host. Therefore the container can use:

```text
http://host.docker.internal:5000
```

to reach the MLflow tracking server on the host.

## Question 8

Yes. After stopping the container and starting another container from the same image, the model should still load correctly as long as the MLflow server and registered model are available.

This demonstrates that the model is not baked into the Docker image. The image contains the serving application and its dependencies, while the model is fetched at runtime from the MLflow Model Registry through the `food11@champion` alias.

Therefore, rebuilding the image is not necessary merely to switch the served model version. The `champion` alias can be reassigned in MLflow.

## Question 9

The Docker image itself still needs to be distributed. Git versions the `Dockerfile`, but another machine cannot automatically obtain the exact built image from Git.

For another machine, CI runner, or Kubernetes cluster to reliably pull the image, the image should be pushed to a container registry such as GitHub Container Registry or Docker Hub and referenced using a versioned tag and preferably an immutable image digest.

The missing step is therefore publishing and versioning the Docker image in a container registry.
