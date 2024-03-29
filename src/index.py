import os
import requests
import time

def initiate_documentation_generation(headers, data):
    url = "https://production-gateway.snorkell.ai/api/app/github/generate/documentation"
    response = requests.post(url, headers=headers, json=data, timeout=600)
    if response.status_code == 200:
        print(response.text)
    else:
        print(f"Request failed: {response.status_code}")
        print(response.text)

def check_documentation_generation_status(headers, data):
    url = "https://production-gateway.snorkell.ai/api/app/github/generate/documentation/status"
    old_status = ""
    count = 0
    while True:
        response = requests.post(url, headers=headers, json=data, timeout=600)
        if response.status_code == 200:
            message = response.text
            if message != old_status:
                print(message)
                old_status = message
                count = 0
            
            count += 1
            if count > 180: # 15 minutes
                print("Documentation generation timed out")
                return
            if message == "COMPLETED":
                print("Documentation generation completed")
                return
        else:
            print(f"Request failed: {response.status_code}")
            print(response.text)
            print("Fetching documentation generation status failed")
            # send slack message to server that documentation generation failed
            return
        time.sleep(5)

def main():
    required_env_vars = ['SNORKELL_API_KEY', 'SNORKELL_CLIENT_ID', 'GITHUB_REPOSITORY', 'BRANCH_NAME', 'GITHUB_SHA', 'COMMIT_MSG']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    headers = {
        'api-key': os.getenv('SNORKELL_API_KEY'),  # Replace with your API key
        'Content-Type': 'application/json'
    }
    data = {
        "installation_id": os.getenv('SNORKELL_CLIENT_ID'),  # Replace with your client ID
        "full_repo_name": os.getenv('GITHUB_REPOSITORY'),   # Replace with your repository name
        "base_branch": os.getenv('BRANCH_NAME'),            # Replace with your branch name
        "commit_sha": os.getenv('GITHUB_SHA'),              # Replace with your commit SHA
        "commit_message": os.getenv('COMMIT_MSG')   # Replace with your commit message
    }
    
    try:
        initiate_documentation_generation(headers, data)
        check_documentation_generation_status(headers, data)
    except requests.exceptions.Timeout:
        print("Request timed out")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
