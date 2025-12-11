import importlib.util
import os


def load_module_from_path(path):
    spec = importlib.util.spec_from_file_location("filterservice_v2", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if __name__ == '__main__':
    script_dir = os.path.dirname(__file__)
    # Use db_helpers (no FastAPI imports) to validate DB connectivity and logic
    helper = load_module_from_path(os.path.join(script_dir, 'db_helpers.py'))

    print('Fetching MCQs for Python / Easy')
    mcqs = helper.fetch_mcqs('Python', 'Easy')
    print(f'Found {len(mcqs)} MCQs')
    for m in mcqs[:3]:
        print('-', m['question_text'])

    print('\nFetching coding questions with label "hashmap" or title match "substring"')
    coding = helper.fetch_coding_questions(title='substring', labels=['hashmap'], difficulty=None)
    print(f'Found {len(coding)} coding questions')
    for c in coding[:3]:
        print('-', c.get('title'))
