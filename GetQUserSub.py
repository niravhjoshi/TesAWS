import boto3
from typing import Set, Dict, List

class AmazonQUserManager:
    def __init__(self, identity_store_region: str = 'us-east-1'):
        self.identity_store_session = boto3.Session(region_name=identity_store_region)
        self.sso_admin_client = self.identity_store_session.client('sso-admin')
        self.identity_store_client = self.identity_store_session.client('identitystore')
        self.identity_store_id = self._get_identity_store_id()

    def _get_identity_store_id(self) -> str:
        response = self.sso_admin_client.list_instances()
        return response['Instances'][0]['IdentityStoreId']

    def get_group_users(self, application_arn: str) -> Dict[str, List[Dict]]:
        result = {'groups': [], 'total_users': 0}
        
        try:
            # Get groups with Q Developer access
            paginator = self.sso_admin_client.get_paginator('list_application_assignments')
            assignments_iterator = paginator.paginate(ApplicationArn=application_arn)

            for page in assignments_iterator:
                for assignment in page['ApplicationAssignments']:
                    if assignment['PrincipalType'] == 'GROUP':
                        group_id = assignment['PrincipalId']
                        
                        # Get group details
                        group_info = self.identity_store_client.describe_group(
                            IdentityStoreId=self.identity_store_id,
                            GroupId=group_id
                        )
                        
                        group_users = []
                        # Get users in the group
                        paginator = self.identity_store_client.get_paginator('list_group_memberships')
                        memberships_iterator = paginator.paginate(
                            IdentityStoreId=self.identity_store_id,
                            GroupId=group_id
                        )
                        
                        for membership_page in memberships_iterator:
                            for membership in membership_page['GroupMemberships']:
                                user_id = membership['MemberId']['UserId']
                                try:
                                    user = self.identity_store_client.describe_user(
                                        IdentityStoreId=self.identity_store_id,
                                        UserId=user_id
                                    )
                                    user_info = {
                                        'UserId': user_id,
                                        'Username': user.get('UserName'),
                                        'Email': user.get('Emails', [{}])[0].get('Value'),
                                        'DisplayName': user.get('DisplayName')
                                    }
                                    group_users.append(user_info)
                                except Exception as e:
                                    print(f"Error getting details for user {user_id}: {str(e)}")
                        
                        group_data = {
                            'GroupId': group_id,
                            'GroupName': group_info['Group']['DisplayName'],
                            'UserCount': len(group_users),
                            'Users': group_users
                        }
                        result['groups'].append(group_data)
                        result['total_users'] += len(group_users)

            return result

        except Exception as e:
            print(f"Error getting Q Developer users: {str(e)}")
            return {'groups': [], 'total_users': 0}

def main():
    # Initialize the manager
    manager = AmazonQUserManager()
    
    # Replace with your actual Amazon Q Developer application ARN
    #application_arn = "arn:aws:sso::ACCOUNT_ID:application/ssoins-XXXXX/apl-XXXXX"
    application_arn = "arn:aws:sso::985539799335:application/ssoins-722359b9176d9db1/apl-434808f3de7d043d"
    
    # Get and display users
    result = manager.get_group_users(application_arn)
    
    print("\nAmazon Q Developer Group Access Summary:")
    print("---------------------------------------")
    print(f"Total Users Across All Groups: {result['total_users']}")
    print("\nGroup Details:")
    
    for group in result['groups']:
        print(f"\nGroup Name: {group['GroupName']}")
        print(f"Group ID: {group['GroupId']}")
        print(f"Number of Users: {group['UserCount']}")
        print("\nUsers in this group:")
        for user in group['Users']:
            print(f"- {user['DisplayName']} ({user['Email']})")
        print("---------------------------------------")

if __name__ == "__main__":
    main()
import boto3
import traceback
from typing import Set

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

    def get_user_details(self, user_id: str) -> dict:
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
                'DisplayName': response.get('DisplayName')
            }
        except Exception as e:
            print(f"Error getting details for user {user_id}: {str(e)}")
            return {'UserId': user_id}

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
    
    # Replace with your actual CodeWhisperer application ARN
    application_arn = "arn:aws:sso::985539799335:application/ssoins-722359b9176d9db1/apl-434808f3de7d043d"
    
    # Get and display users
    users = manager.get_codewhisperer_users(application_arn)
    
    print("\nAmazonQ Developer Users:")
    print("-------------------")
    for user in users:
        user_dict = dict(user)
        print(f"User ID: {user_dict.get('UserId')}")
        print(f"Username: {user_dict.get('Username')}")
        print(f"Email: {user_dict.get('Email')}")
        print(f"Display Name: {user_dict.get('DisplayName')}")
        print("-------------------")

if __name__ == "__main__":
    main()
