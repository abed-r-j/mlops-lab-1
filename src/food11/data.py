from pathlib import Path
from shutil import copy2
from PIL import Image


CATEGORIES = {
    0: "Bread",
    1: "Dairy product",
    2: "Dessert",
    3: "Egg",
    4: "Fried food",
    5: "Meat",
    6: "Noodles-Pasta",
    7: "Rice",
    8: "Seafood",
    9: "Soup",
    10: "Vegetable-Fruit",
}

SPLITS = ("training", "evaluation", "validation")

RAW_ROOT = Path("data/food11_raw")
PROCESSED_ROOT = Path("data/food11_processed")
MINI_ROOT = Path("data/food11_processed_mini")

IMAGE_SIZE = (128, 128)
MINI_LIMIT = 100

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def get_category(filename: str) -> str:
    """Extract the Food-11 category from the beginning of the filename."""
    prefix = filename.split("_", 1)[0]

    try:
        category_id = int(prefix)
    except ValueError as exc:
        raise ValueError(
            f"Could not determine category from filename: {filename}"
        ) from exc

    if category_id not in CATEGORIES:
        raise ValueError(
            f"Unknown Food-11 category ID {category_id} in {filename}"
        )

    return CATEGORIES[category_id]


def process_image(
    source: Path,
    destination: Path,
) -> None:
    """Resize an image to 128x128 and save it to the destination."""
    destination.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(source) as image:
        image = image.convert("RGB")
        image = image.resize(IMAGE_SIZE)

        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination)


def process_dataset(
    output_root: Path,
    mini: bool = False,
) -> None:
    """Convert the raw Food-11 structure into category-based folders."""

    for split in SPLITS:
        source_split = RAW_ROOT / split

        if not source_split.exists():
            raise FileNotFoundError(
                f"Missing input directory: {source_split}"
            )

        # Keep deterministic ordering so that the mini dataset
        # is reproducible.
        images = sorted(
            path
            for path in source_split.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        )

        category_counts: dict[str, int] = {}

        for source in images:
            category = get_category(source.name)

            current_count = category_counts.get(category, 0)

            if mini and current_count >= MINI_LIMIT:
                continue

            destination = (
                output_root
                / split
                / category
                / source.name
            )

            process_image(source, destination)

            category_counts[category] = current_count + 1

        print(f"Processed {split}:")
        for category, count in sorted(category_counts.items()):
            print(f"  {category}: {count}")


def main() -> None:
    print("Creating full processed dataset...")
    process_dataset(PROCESSED_ROOT, mini=False)

    print("\nCreating mini processed dataset...")
    process_dataset(MINI_ROOT, mini=True)

    print("\nFinished processing Food-11.")


if __name__ == "__main__":
    main()