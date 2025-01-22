import boto3
import traceback
import csv
from typing import Set, List

class CodeWhispererUserManager:
    def __init__(self, identity_store_region: str = 'us-east-1'):
        # Initialize sessions and clients
        self.identity_store_session = boto3.Session(region_name=identity_store_region)
        self.sso_admin_client = self.identity_store_session.client('sso-admin')
        self.identity_store_client = self.identity_store_session.client('identitystore')
        self.identity_store_id = self._get_identity_store_id()

    def _get_identity_store_id(self) -> str:
        """Retrieve the Identity Store ID from SSO instance"""
        response = self.sso_admin_client.list_instances()
        return response['Instances'][0]['IdentityStoreId']

    def get_user_details(self, user_id: str,last_act_date: str) -> dict:
        """Get user details from Identity Store"""
        try:
            response = self.identity_store_client.describe_user(
                IdentityStoreId=self.identity_store_id,
                UserId=user_id
            )
            return {
                'UserId': user_id,
                'Username': response.get('UserName'),
                'Email': response.get('Emails', [{}])[0].get('Value'),
                'DisplayName': response.get('DisplayName'),
                "LastActivityDate":last_act_date
            }
        except Exception as e:
            print(f"Error getting details for user {user_id}: {str(e)}")
            return {'UserId': user_id}

    def get_users_from_csv(self, csv_file_path: str) -> List[dict]:
        """Get user details for all UserIDs provided in CSV file"""
        user_details_list = []
        
        try:
            with open(csv_file_path, 'r') as file:
                csv_reader = csv.reader(file)
                # Skip header if exists
                next(csv_reader, None)
                
                for row in csv_reader:
                    if row:  # Check if row is not empty
                        user_id = row[0].strip()  # Assuming UserID is in first column
                        latest_activity_date = row[1] #second date column
                        user_details = self.get_user_details(user_id,latest_activity_date)
                        print(user_details)
                        user_details_list.append(user_details)
        except FileNotFoundError:
            print(f"Error: CSV file not found at {csv_file_path}")
        except Exception as e:
            print(f"Error processing CSV file: {str(e)}")
            traceback.print_exc()
        # print (user_details_list)    
        return user_details_list

    def get_codewhisperer_users(self, application_arn: str) -> Set[dict]:
        """Get all users with CodeWhisperer access"""
        users = set()
        group_ids = set()

        try:
            # Get direct assignments
            paginator = self.sso_admin_client.get_paginator('list_application_assignments')
            assignments_iterator = paginator.paginate(ApplicationArn=application_arn)

            # Collect users and groups
            for page in assignments_iterator:
                for assignment in page['ApplicationAssignments']:
                    if assignment['PrincipalType'] == 'USER':
                        users.add(assignment['PrincipalId'])
                    elif assignment['PrincipalType'] == 'GROUP':
                        group_ids.add(assignment['PrincipalId'])

            # Get users from groups
            for group_id in group_ids:
                try:
                    paginator = self.identity_store_client.get_paginator('list_group_memberships')
                    memberships_iterator = paginator.paginate(
                        IdentityStoreId=self.identity_store_id,
                        GroupId=group_id
                    )
                    
                    for page in memberships_iterator:
                        for membership in page['GroupMemberships']:
                            users.add(membership['MemberId']['UserId'])
                except Exception as e:
                    print(f"Error processing group {group_id}: {str(e)}")

            # Get detailed information for all users
            user_details = set()
            for user_id in users:
                user_details.add(frozenset(self.get_user_details(user_id).items()))

            return user_details

        except Exception as e:
            print(f"Error getting CodeWhisperer users: {str(e)}")
            traceback.print_exc()
            return set()

def main():
    # Initialize the manager
    manager = CodeWhispererUserManager()
    
    # Get CSV file path as input
    csv_file_path = input("Enter the path to your CSV file containing UserIDs: ")
    
    # Get and display users
    users = manager.get_users_from_csv(csv_file_path)
    
    # print("\nUser Details:")
    # print("-------------------")
    
    # Create output CSV file
    output_file_path = "user_details_output.csv"
    try:
        with open(output_file_path, 'w', newline='') as output_file:
            fieldnames = ['UserId', 'Username', 'Email', 'DisplayName','LastActivityDate']
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write user details and print to console
            for user in users:
                writer.writerow(user)
                # print(f"User ID: {user.get('UserId')}")
                # print(f"Username: {user.get('Username')}")
                # print(f"Email: {user.get('Email')}")
                # print(f"Display Name: {user.get('DisplayName')}")
                # print("-------------------")
                
        print(f"\nResults have been saved to {output_file_path}")
        
    except Exception as e:
        print(f"Error writing to output file: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
