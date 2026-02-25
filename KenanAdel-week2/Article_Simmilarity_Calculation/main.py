from processor import TextProcessor
from similarity import SimilarityModel
import os

def main():
    csv_file = 'articles.csv'
    pkl_file = 'similarities.pkl'
    
    if not os.path.exists(csv_file):
        print(f" '{csv_file}' not found in the current directory")
        return

    processor = TextProcessor(csv_file)
    articles = processor.read_and_clean_data()

    model = SimilarityModel(articles)
    model.build_vocabulary()
    model.generate_vectors()
    model.calculate_cosine_similarity()

    print(f"--> Saving similarity matrix to '{pkl_file}'...")
    model.save_similarities(pkl_file)
    print("--> Saved successfully\n")

    print("=" * 50)
    print("               Testing Phase              ")
    print("=" * 50)

    while True:
        test_id = input("\n --> Enter Article ID for Testing: ").strip()
        print(f"\n--- Top 3 Similar Articles for ID '{test_id}' ---")
        
        try:
            top_3 = model.get_top_3_similar_articles(test_id)
            idx = 1 
            for title, score in top_3:
                print(f"  {idx}. {title} (Similarity: {score:.2f}%)")
                idx += 1 
        except ValueError as e:
            print(f"--> Error: {e}")
            
        print("-" * 35)
        continue_search = input(" Do you want to search for another ID? only choose (y/n): ").strip().lower()
        
        if continue_search != 'y':
            break
            
    print("\n" + "=" * 50)
    print("   --> Processing Complete See u later!   ")
    print("=" * 50)

if __name__ == '__main__':
    main()