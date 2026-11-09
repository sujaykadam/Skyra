import argparse
import json
import os


def main():
    parser = argparse.ArgumentParser(description="Prepare ViF-Bench index files for local use")

    parser.add_argument(
        "--index_json",
        type=str,
        required=True,
        help="Path to the original test_index.json shipped with ViF-Bench."
    )

    parser.add_argument(
        "--frames_dir",
        type=str,
        required=True,
        help="Path to the extracted parsed_frames directory."
    )

    parser.add_argument(
        "--save_dir",
        type=str,
        default="./data",
        help="Directory to save the generated index files."
    )

    parser.add_argument(
        "--smoke_models",
        type=str,
        nargs="+",
        default=["sora-2", "Wan2.2-T2V-14B"],
        help="AIGC models included in the small smoke-test index."
    )

    parser.add_argument(
        "--smoke_num",
        type=int,
        default=5,
        help="Number of real/fake pairs per AIGC model in the smoke-test index."
    )

    args = parser.parse_args()

    frames_dir = os.path.abspath(args.frames_dir)
    os.makedirs(args.save_dir, exist_ok=True)

    with open(args.index_json, 'r') as f:
        index_data_ = json.load(f)

    # Replace the placeholder root with the local frames directory
    index_data = {}
    for k, v in index_data_.items():
        index_data[k] = [p.replace("path_to_parsed_frames_dir", frames_dir) for p in v]

    full_path = os.path.join(args.save_dir, "index_full.json")
    with open(full_path, 'w') as f:
        json.dump(index_data, f, indent=4)
    print(f"Full index: {sum(len(v) for v in index_data.values())} videos -> {full_path}")

    # Keep only base ids present for 'Real' and every smoke model, so eval.py can pair them
    base_ids = [os.path.basename(p) for p in index_data["Real"]]
    for aigc_model in args.smoke_models:
        available = {os.path.basename(p) for p in index_data[aigc_model]}
        base_ids = [i for i in base_ids if i in available]
    base_ids = set(base_ids[:args.smoke_num])

    smoke_data = {}
    for aigc_model in ["Real"] + args.smoke_models:
        smoke_data[aigc_model] = [p for p in index_data[aigc_model] if os.path.basename(p) in base_ids]

    smoke_path = os.path.join(args.save_dir, "index_smoke.json")
    with open(smoke_path, 'w') as f:
        json.dump(smoke_data, f, indent=4)
    print(f"Smoke index: {sum(len(v) for v in smoke_data.values())} videos -> {smoke_path}")


if __name__ == "__main__":
    main()
