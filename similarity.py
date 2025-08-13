import json
from pathlib import Path
from PIL import Image
import imagehash
import os
import re  # Add this import for regular expressions
import shutil
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from tqdm import tqdm

class JsonPromptManager:
    def __init__(self, json_path):
        self.json_path = json_path
        self.prompts = self._load_prompts()
        
    def _load_prompts(self):
        """Load prompts from JSON file"""
        with open(self.json_path, 'r') as f:
            return json.load(f)
    
    def get_chapter_prompts(self, chapter_key):
        """Get all prompts for a specific chapter"""
        if chapter_key not in self.prompts:
            raise ValueError(f"Chapter '{chapter_key}' not found in prompts")
        return self.prompts[chapter_key]
    
    def get_prompt_by_unique_name(self, chapter_key, unique_name):
        """Get prompt for a specific unique_name in a chapter"""
        chapter_prompts = self.get_chapter_prompts(chapter_key)
        for prompt in chapter_prompts:
            if prompt["unique_name"] == unique_name:
                return prompt
        raise ValueError(f"Unique name '{unique_name}' not found in chapter '{chapter_key}'")

class ImageSelector:
    def __init__(self):
        pass
        
    def get_image_similarity_score(self, image_path, reference_image_path):
        """Calculate similarity score between two images using perceptual hash"""
        # Load images
        img1 = Image.open(image_path)
        img2 = Image.open(reference_image_path)
        
        # Calculate perceptual hashes
        hash1 = imagehash.average_hash(img1)
        hash2 = imagehash.average_hash(img2)
        
        # Calculate similarity (0 = identical, higher = more different)
        similarity = hash1 - hash2
        
        # Convert to similarity score (0 to 1, where 1 is most similar)
        max_possible_difference = 64  # Maximum possible difference for 8x8 hash
        similarity_score = 1 - (similarity / max_possible_difference)
        
        return similarity_score
    
    def find_matching_images(self, directory, base_filename):
        """Find all images that match the base filename pattern"""
        # Create pattern for matching filenames
        pattern = re.compile(rf"{base_filename}(?:_[2-4])?\.jpg$")
        
        # Get all matching files
        matching_files = []
        for file in Path(directory).glob("*.jpg"):
            if pattern.match(file.name):
                matching_files.append(file)
        
        return sorted(matching_files)
    
    def select_best_image(self, image_dir, unique_name):
        """Select the best image from existing images in a directory"""
        # Find all matching images
        image_files = self.find_matching_images(image_dir, unique_name)
        
        if not image_files:
            raise ValueError(f"No matching images found for pattern: {unique_name}")
            
        print(f"Found {len(image_files)} matching images:")
        for img in image_files:
            print(f"- {img.name}")
        
        # Calculate similarity scores for each image
        scores = []
        for img_path in image_files:
            try:
                # Calculate average similarity with all other images
                total_similarity = 0
                comparison_count = 0
                
                for other_img in image_files:
                    if other_img != img_path:
                        score = self.get_image_similarity_score(str(img_path), str(other_img))
                        total_similarity += score
                        comparison_count += 1
                
                # Calculate average similarity
                avg_similarity = total_similarity / comparison_count if comparison_count > 0 else 0
                scores.append((img_path, avg_similarity))
                print(f"Image: {img_path.name}, Average Similarity Score: {avg_similarity:.4f}")
            except Exception as e:
                print(f"Error processing {img_path}: {str(e)}")
        
        if not scores:
            raise ValueError("No valid images could be processed")
        
        # Sort by similarity score in descending order
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return the best image path and its score
        best_image_path = scores[0][0]
        best_score = scores[0][1]
        
        return str(best_image_path), best_score

def calculate_similarity(img1, img2):
    # Convert images to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Calculate SSIM
    similarity = ssim(gray1, gray2)
    return similarity

def get_base_filename(filename):
    # Remove _2, _3, _4 from the end of filename
    return re.sub(r'_[234]\.(jpg|jpeg|png)$', r'.\1', filename)

def find_best_image_in_set(image_paths):
    if not image_paths:
        return None, 0
    
    best_image = None
    best_score = -1
    
    # Compare each image with all others
    for img_path in image_paths:
        try:
            img = cv2.imread(img_path)
            if img is None:
                continue
                
            total_similarity = 0
            comparison_count = 0
            
            # Compare with all other images
            for other_path in image_paths:
                if other_path != img_path:
                    other_img = cv2.imread(other_path)
                    if other_img is None:
                        continue
                        
                    # Resize images to match dimensions
                    img_resized = cv2.resize(img, (other_img.shape[1], other_img.shape[0]))
                    
                    # Calculate similarity
                    similarity = calculate_similarity(img_resized, other_img)
                    total_similarity += similarity
                    comparison_count += 1
            
            # Calculate average similarity
            if comparison_count > 0:
                avg_similarity = total_similarity / comparison_count
                if avg_similarity > best_score:
                    best_score = avg_similarity
                    best_image = img_path
                    
        except Exception as e:
            print(f"Error processing {img_path}: {str(e)}")
    
    return best_image, best_score

def process_chapter(video_path):
    # video_path = f"video10/{video}"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    image_sets = {}
    for root, dirs, files in os.walk(video_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                base_name = get_base_filename(file)
                if base_name not in image_sets:
                    image_sets[base_name] = []
                image_sets[base_name].append(os.path.join(root, file))
    results = []
    for base_name, image_paths in tqdm(image_sets.items(), desc=f"Processing image sets for {video_path}"):
        if len(image_paths) > 1:  # Only process if we have multiple images
            best_image, score = find_best_image_in_set(image_paths)
            if best_image:
                # Get just the filename without extension
                best_image_name = os.path.splitext(os.path.basename(best_image))[0]
                creation_time = os.path.getmtime(best_image)
                results.append({
                    'base_name': base_name,
                    'best_image': best_image_name,
                    'creation_time': creation_time
                })
    
    # Sort results by creation time (oldest first)
    results.sort(key=lambda x: x['creation_time'])
    
    # Save results to file
    results_file = os.path.join(output_dir, f"{video_path}_best_images.txt")
    with open(results_file, 'w') as f:
        for result in results:
            f.write(f"{result['best_image']}\n")
    print(f"Results saved to {results_file}")
    print(f"Processed {len(results)} image sets for {video_path}")

def main():
    process_chapter("Video15")
    # for chapter in ["ch7", "ch8", "ch9"]:
    #     process_chapter(chapter)

if __name__ == "__main__":
    main() 