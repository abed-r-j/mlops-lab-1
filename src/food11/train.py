from __future__ import annotations

import argparse
from pathlib import Path

import mlflow
import mlflow.pytorch
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms


NUM_CLASSES = 11
IMAGE_SIZE = 224

TRACKING_URI = "http://127.0.0.1:5000"
EXPERIMENT_NAME = "food11"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train ResNet18 on Food-11 with MLflow tracking."
    )

    parser.add_argument(
        "--dataset",
        choices=["processed", "mini"],
        default="mini",
        help="Dataset to use: processed or mini.",
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=5,
        help="Number of training epochs.",
    )

    parser.add_argument(
        "--lr",
        type=float,
        default=0.001,
        help="Learning rate.",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Training and validation batch size.",
    )

    return parser.parse_args()


def get_transforms():
    train_transform = transforms.Compose(
        [
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )

    evaluation_transform = transforms.Compose(
        [
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )

    return train_transform, evaluation_transform


def create_dataloaders(
    dataset_name: str,
    batch_size: int,
    device: torch.device,
):
    dataset_roots = {
        "processed": Path("data/food11_processed"),
        "mini": Path("data/food11_processed_mini"),
    }

    root = dataset_roots[dataset_name]

    train_dir = root / "training"
    val_dir = root / "validation"
    test_dir = root / "evaluation"

    for directory in (train_dir, val_dir, test_dir):
        if not directory.exists():
            raise FileNotFoundError(
                f"Dataset directory not found: {directory}"
            )

    train_transform, evaluation_transform = get_transforms()

    train_dataset = datasets.ImageFolder(
        train_dir,
        transform=train_transform,
    )

    val_dataset = datasets.ImageFolder(
        val_dir,
        transform=evaluation_transform,
    )

    test_dataset = datasets.ImageFolder(
        test_dir,
        transform=evaluation_transform,
    )

    if len(train_dataset.classes) != NUM_CLASSES:
        raise ValueError(
            f"Expected {NUM_CLASSES} classes, "
            f"found {len(train_dataset.classes)}: "
            f"{train_dataset.classes}"
        )

    print("Classes:", train_dataset.classes)
    print("Training images:", len(train_dataset))
    print("Validation images:", len(val_dataset))
    print("Evaluation images:", len(test_dataset))
    print("Device:", device)

    use_cuda = device.type == "cuda"

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=use_cuda,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=use_cuda,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=use_cuda,
    )

    return train_loader, val_loader, test_loader


def build_model() -> nn.Module:
    weights = models.ResNet18_Weights.DEFAULT

    model = models.resnet18(weights=weights)

    model.fc = nn.Linear(
        model.fc.in_features,
        NUM_CLASSES,
    )

    return model


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    device: torch.device,
) -> float:
    model.train()

    running_loss = 0.0
    total_samples = 0

    for images, labels in loader:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        batch_size = images.size(0)

        running_loss += loss.item() * batch_size
        total_samples += batch_size

    return running_loss / total_samples


@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, float]:
    model.eval()

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)
        loss = criterion(outputs, labels)

        batch_size = images.size(0)

        running_loss += loss.item() * batch_size

        predictions = outputs.argmax(dim=1)

        correct += (predictions == labels).sum().item()
        total += batch_size

    average_loss = running_loss / total
    accuracy = correct / total

    return average_loss, accuracy


def main() -> None:
    args = parse_args()

    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    train_loader, val_loader, test_loader = create_dataloaders(
        dataset_name=args.dataset,
        batch_size=args.batch_size,
        device=device,
    )

    model = build_model().to(device)

    criterion = nn.CrossEntropyLoss()

    optimizer = optim.Adam(
        model.parameters(),
        lr=args.lr,
    )

    with mlflow.start_run() as run:
        mlflow.log_params(
            {
                "dataset": args.dataset,
                "epochs": args.epochs,
                "lr": args.lr,
                "batch_size": args.batch_size,
                "model": "resnet18",
                "num_classes": NUM_CLASSES,
            }
        )

        print(f"Run ID: {run.info.run_id}")

        for epoch in range(1, args.epochs + 1):
            train_loss = train_one_epoch(
                model,
                train_loader,
                criterion,
                optimizer,
                device,
            )

            val_loss, val_accuracy = evaluate(
                model,
                val_loader,
                criterion,
                device,
            )

            mlflow.log_metric(
                "train_loss",
                train_loss,
                step=epoch,
            )

            mlflow.log_metric(
                "val_loss",
                val_loss,
                step=epoch,
            )

            mlflow.log_metric(
                "val_accuracy",
                val_accuracy,
                step=epoch,
            )

            print(
                f"Epoch {epoch}/{args.epochs} | "
                f"train_loss={train_loss:.4f} | "
                f"val_loss={val_loss:.4f} | "
                f"val_accuracy={val_accuracy:.4f}"
            )

        _, test_accuracy = evaluate(
            model,
            test_loader,
            criterion,
            device,
        )

        mlflow.log_metric(
            "test_accuracy",
            test_accuracy,
        )

        mlflow.pytorch.log_model(
            model,
            name="model",
            serialization_format="pickle",
        )

        print(f"Final test accuracy: {test_accuracy:.4f}")
        print(f"Run ID: {run.info.run_id}")


if __name__ == "__main__":
    main()