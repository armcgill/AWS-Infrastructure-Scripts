# report for AWS Workspace Usage
import boto3
from datetime import date, datetime

# const
THRESHOLD_DAYS = 180  # Adjust the threshold to your desired date

# running counts
running_count = 0
non_used_count = 0
threshold_count = 0


def run_it(message):

    print(f'{message}')
    #Establish connection to workspaces
    aws = boto3.session.Session()
    client = aws.client('workspaces')
    response = client.describe_workspaces()
    workspaces = response['Workspaces']

    print_workspace(client, workspaces)
    while "NextToken" in response:
        response = client.describe_workspaces(NextToken=response["NextToken"])
        workspaces = response['Workspaces']
        print_workspace(client, workspaces)
    #Print totals 
    print('')
    print(f'Total Workspaces: {running_count}')
    print(f'Never Been Used Count: {non_used_count}')
    print(f'Past threshold Count: {threshold_count} haven\'t been used in the last {THRESHOLD_DAYS} days ')


def print_workspace(client, workspaces):
    workspaceIds = [workspace['WorkspaceId'] for workspace in workspaces] # List of WorkspaceIds
    response = client.describe_workspaces_connection_status(WorkspaceIds=workspaceIds)
    statuses = response['WorkspacesConnectionStatus'] # list of Connection Stauses
    for status in statuses:
        workspaceId = status["WorkspaceId"]
        user_name = get_user_for_workspace(workspaceId, workspaces)
        tags = client.describe_tags(ResourceId = workspaceId)
        get_workspace_tags(tags)
        if "LastKnownUserConnectionTimestamp" not in status:
            # no known usage, so they've never used it
            print_usage(-1, workspaceId, user_name)

        else:
            tmp = status['LastKnownUserConnectionTimestamp']
            last_used_date = tmp.replace(tzinfo=None)
            today = datetime.now()
            delta = today - last_used_date
            print_usage(delta.days, workspaceId, user_name)

def get_workspace_tags(tags): 
        try:
            for i in range(3): # In this case my workspace had 3 tags: Replace with your number of tags
                tagList = tags['TagList'][i]
                print('  ' + tagList['Key'] + ' -- ' + tagList['Value'])
        except IndexError:
            print("   No tags Found")       

def print_usage(days, workspace_id, user):
    print(f'{days}, {workspace_id} ,{user}')

    global running_count
    global non_used_count
    global threshold_count
    global THRESHOLD_DAYS
    running_count += 1

    if days < 0:
        non_used_count += 1
    if days > THRESHOLD_DAYS:
        threshold_count += 1


def get_user_for_workspace(workspace_id, workspaces):
    for workspace in workspaces:
        if workspace["WorkspaceId"] == workspace_id:
            return workspace["UserName"]

    return ""



if __name__ == '__main__':
    run_it('AWS Workspace Usage Report')