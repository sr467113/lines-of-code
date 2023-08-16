import requests
import base64
from datetime import datetime
import csv

# Azure DevOps organization URL
organization_url = 'ENTER_YOUR_ORG_URL'


# Personal access token (PAT) with appropriate permissions
personal_access_token = 'ENTER_YOUR_PAT'

# Target month for the report
target_month = 'TARGET_MONTH'

# Convert target month to start and end dates
target_date = datetime.strptime(target_month, '%Y-%m')
start_date = target_date.replace(day=1).strftime('%Y-%m-%d')
end_date = target_date.replace(day=30).strftime('%Y-%m-%d')



username = 'ENTER_YOUR_USERNAME'
password = 'ENTER_YOUR_PASSWORD'
credentials = base64.b64encode(f'{username}:{password}'.encode('utf-8')).decode('utf-8')

# API request URL
url = f'{organization_url}/_apis/git/repositories'

# Request headers with authentication
headers = {
    'Authorization': 'Basic ' + credentials 
}


# Dictionary to store lines of code by developer
lines_of_code = {}

# Create a list to store the developer details
developer_details = []

# Retrieve all projects in the organization
response = requests.get(url, headers=headers)
projects = response.json().get('value', [])

# Iterate through projects
for project in projects:
    project_name = project.get('name')
    project_id = project.get('project', {}).get('id')
    # print(project_id)

    # API request URL for project repositories
    project_repos_url = f'{organization_url}/{project_id}/_apis/git/repositories'


    # Make API request to retrieve repositories in the project
    response = requests.get(project_repos_url, headers=headers)
    repositories = response.json().get('value', [])
    print(response)

    # Iterate through repositories
    for repository in repositories:
        repository_name = repository.get('name')
        repository_id = repository.get('id')
        print(repository_id)

        # API request URL for repository commits
        repo_commits_url = f'{url}/{repository_id}/commits'

        # API query parameters
        query_params = {
            'searchCriteria.fromDate': start_date,
            'searchCriteria.toDate': end_date
        }

        # Make API request to retrieve commits in the specified month
        response = requests.get(repo_commits_url, headers=headers, params=query_params)
        commits = response.json().get('value', [])

        # Iterate through commits
        for commit in commits:
            author = commit.get('author', {}).get('name')
            change_counts = commit.get('changeCounts', {})

            if author not in lines_of_code:
                lines_of_code[author] = {
                    'Add': 0,
                    'Edit': 0,
                    'Delete': 0
                }

            lines_of_code[author]['Add'] += change_counts.get('Add', 0)
            lines_of_code[author]['Edit'] += change_counts.get('Edit', 0)
            lines_of_code[author]['Delete'] += change_counts.get('Delete', 0)

# Print lines of code report
for developer, counts in lines_of_code.items():
    total_lines = counts['Add'] + counts['Edit'] + counts['Delete']
    print(f'{developer}: Total Lines={total_lines}, Add={counts["Add"]}, Edit={counts["Edit"]}, Delete={counts["Delete"]}')
    

# Iterate through developers and lines_of_code dictionary
for developer, lines in lines_of_code.items():
    # print(f'{developer} : {lines}')

    add_count = lines.get('Add', 0)
    edit_count = lines.get('Edit', 0)
    delete_count = lines.get('Delete', 0)
    total_lines = add_count + edit_count + delete_count
    
    developer_details.append({
        'Developer': developer,
        'Total Lines': total_lines,
        'Add': add_count,
        'Edit': edit_count,
        'Delete': delete_count
    })

# Define the CSV file path
csv_file = 'developer_details.csv'

# Write the developer details to the CSV file
with open(csv_file, 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['Developer', 'Total Lines', 'Add', 'Edit', 'Delete'])
    writer.writeheader()
    writer.writerows(developer_details)

print(f'Developer details written to {csv_file}')
