# 🍿 Popcorn Quiz
Welcome to Popcorn Quiz! This is a fun movie trivia game you can play right from your terminal. Test your movie knowledge and see how you stack up against others!

## What's Inside
- Popcorn Quiz Code: The Python script that runs the game. Just fire it up in your terminal to start playing.
- Ranking File: A file to keep track of high scores, so you can always strive to beat the best!

## How to Play
1. **Clone the repository** to your local machine.
2. **Navigate to the directory** where you cloned the repo.
3. **Set up your TMDB API Key**:
    1. [Sign up](https://www.themoviedb.org/) for a free account on The Movie Database (TMDB) if you don't have one.
    2. Log in to your TMDB account and go to the [API section](https://www.themoviedb.org/settings/api).
    3. Click on "Create API Key" and follow the instructions to get your API key.
    4. Create a file named .env in the project directory and add the following line to it:
     ```
     TMDB_API_KEY=your_api_key_here
     ```
    5. Replace `your_api_key_here` with the actual API key you obtained.
4. **Install dependencies** (if needed):
   ```
   pip install -r requirements.txt
   ```
6. **Run the Python script**:
  ```
  python Popcorn quiz.py
  ```
6. **Answer the movie trivia questions** and see your score at the end!

## High Scores
The game saves your best scores in a ranking file. Challenge yourself and your friends to see who can get the highest score!

## Note on API Performance
Popcorn Quiz uses the API of The Movie Database (TMDB) to fetch movie data. Occasionally, you might experience slow loading times if the API is not functioning optimally at that moment. Thanks for your patience and understanding!

Enjoy the quiz and have fun! 🎬🍿
