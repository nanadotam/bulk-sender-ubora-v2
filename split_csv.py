import pandas as pd
import math
import os

def split_csv(input_file, chunk_size=40, output_folder="chunks"):
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)

    # Load the CSV
    df = pd.read_csv(input_file)
    total_rows = len(df)

    # Calculate number of chunk files
    num_chunks = math.ceil(total_rows / chunk_size)

    print(f"Total rows: {total_rows}")
    print(f"Creating {num_chunks} chunk files...")

    # Generate chunk files
    for i in range(num_chunks):
        start = i * chunk_size
        end = start + chunk_size

        chunk = df.iloc[start:end]
        output_path = os.path.join(output_folder, f"chunk_{i+1}.csv")
        chunk.to_csv(output_path, index=False)

        print(f"✓ Saved {output_path} ({len(chunk)} rows)")

    print("\n🎉 Done! All chunks created.")

# ================================
# RUN SCRIPT
# ================================
if __name__ == "__main__":
    split_csv("input.csv", chunk_size=40)
