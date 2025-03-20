import boto3
import csv
from datetime import datetime

class IdentityCenterUserExporter:
    def __init__(self, region_name='us-east-1'):
        self.region_name = region_name
        self.sso_admin_client = boto3.client('sso-admin', region_name=region_name)
        self.identity_store_client = None
        self.identity_store_id = None
        
    def initialize(self):
        """Initialize the identity store client and get the identity store ID"""
        try:
            # Get the Identity Store ID for the SSO instance
            response = self.sso_admin_client.list_instances()
            
            if not response.get('Instances'):
                print("No Identity Center instances found. Verify your permissions and region.")
                return False
                
            # Use the first instance by default
            self.identity_store_id = response['Instances'][0]['IdentityStoreId']
            self.identity_store_client = boto3.client('identitystore', region_name=self.region_name)
            return True
        except Exception as e:
            print(f"Error initializing Identity Center: {e}")
            return False
    
    def get_application_users(self, application_arn):
        """Get users assigned to a specific application"""
        if not self.identity_store_id:
            if not self.initialize():
                return []
        
        try:
            print(f"Retrieving application assignments for {application_arn}...")
            user_ids = set()
            
            # Use list_application_assignment_configurations instead of pagination
            # since list_application_assignments doesn't have a paginator
            next_token = None
            while True:
                if next_token:
                    response = self.sso_admin_client.list_application_assignments(
                        ApplicationArn=application_arn,
                        MaxResults=100,
                        NextToken=next_token
                    )
                else:
                    response = self.sso_admin_client.list_application_assignments(
                        ApplicationArn=application_arn,
                        MaxResults=100
                    )
                
                for assignment in response.get('ApplicationAssignments', []):
                    if assignment.get('PrincipalType') == 'USER':
                        user_ids.add(assignment.get('PrincipalId'))
                
                next_token = response.get('NextToken')
                if not next_token:
                    break
            
            print(f"Found {len(user_ids)} user assignments. Retrieving user details...")
            
            # Get detailed user information for each user ID
            users_data = []
            for user_id in user_ids:
                try:
                    user = self.identity_store_client.describe_user(
                        IdentityStoreId=self.identity_store_id,
                        UserId=user_id
                    )
                    
                    user_data = {
                        'UserId': user_id,
                        'Username': user.get('UserName', ''),
                        'Email': next((item.get('Value', '') for item in user.get('Emails', []) 
                                    if item.get('Primary', False)), ''),
                        'FirstName': user.get('Name', {}).get('GivenName', ''),
                        'LastName': user.get('Name', {}).get('FamilyName', ''),
                        'DisplayName': user.get('DisplayName', '')
                    }
                    users_data.append(user_data)
                except Exception as e:
                    print(f"Error getting user details for {user_id}: {e}")
            
            return users_data
        except Exception as e:
            print(f"Error getting application users: {e}")
            return []
    
    def export_to_csv(self, users_data, filename=None):
        """Export user data to a CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"application_users_{timestamp}.csv"
        
        if not users_data:
            print("No user data to export")
            return
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = users_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for user in users_data:
                    writer.writerow(user)
            
            print(f"User data exported to {filename}")
        except Exception as e:
            print(f"Error exporting to CSV: {e}")

def main():
    # Replace with your application ARN
    application_arn = "arn:aws:sso::1234:application/ssoins-1234/apl-1234"
    
    # Optional: specify your AWS region if different from default
    region_name = "us-east-1"  # Change to your Identity Center region
    
    exporter = IdentityCenterUserExporter(region_name)
    print(f"Retrieving users for application: {application_arn}")
    users_data = exporter.get_application_users(application_arn)
    
    print(f"Found {len(users_data)} users assigned to the application")
    exporter.export_to_csv(users_data)

if __name__ == "__main__":
    main()
