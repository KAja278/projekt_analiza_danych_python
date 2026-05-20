import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def main():
    path_to_data = os.path.join("data", "processed", "ZBIORCZY_raport_clickbaitu.csv")
    
    if not os.path.exists(path_to_data):
        print(f"Błąd: Nie znaleziono pliku {path_to_data}! Uruchom najpierw src/analyzer.py")
        return

    df = pd.read_csv(path_to_data)
    
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    
    ax = sns.boxplot(
        x="channel_name", 
        y="clickbait_score", 
        data=df, 
        palette="Set2",
        hue="channel_name",
        legend=False
    )
    
    plt.title("Porównanie poziomu Clickbaitu na polskich kanałach YouTube", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Nazwa Kanału", fontsize=12, labelpad=10)
    plt.ylabel("Punkty Clickbaitu (Skala 0-22)", fontsize=12, labelpad=10)
    plt.ylim(-0.5, 22.5)

    os.makedirs("plots", exist_ok=True)
    output_image_path = os.path.join("plots", "porownanie_clickbaitu_boxplot.png")
    plt.tight_layout()
    plt.savefig(output_image_path, dpi=300)
    plt.close()

    print("-" * 50)
    print("Sukces! Wykres podglądowy został wygenerowany.")
    print(f"Znajdziesz go tutaj: {output_image_path}")

if __name__ == "__main__":
    main()