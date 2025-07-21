import json
import os
from datetime import datetime
from config import DATABASE_FILE

class Database:
    def __init__(self):
        self.data = self.load_data()
    
    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(DATABASE_FILE):
            try:
                with open(DATABASE_FILE, 'r') as f:
                    return json.load(f)
            except:
                return self.get_default_data()
        return self.get_default_data()
    
    def get_default_data(self):
        """Return default database structure"""
        return {
            'users': {},
            'pending_links': [],
            'approved_links': []
        }
    
    def save_data(self):
        """Save data to JSON file"""
        try:
            with open(DATABASE_FILE, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def add_user(self, user_id, username=None, first_name=None):
        """Add or update user in database"""
        user_id = str(user_id)
        if user_id not in self.data['users']:
            self.data['users'][user_id] = {
                'username': username,
                'first_name': first_name,
                'joined_at': datetime.now().isoformat(),
                'has_access': False,
                'last_check': None
            }
        else:
            # Update user info
            self.data['users'][user_id]['username'] = username
            self.data['users'][user_id]['first_name'] = first_name
        
        self.save_data()
    
    def grant_access(self, user_id):
        """Grant access to user"""
        user_id = str(user_id)
        if user_id in self.data['users']:
            self.data['users'][user_id]['has_access'] = True
            self.data['users'][user_id]['last_check'] = datetime.now().isoformat()
            self.save_data()
    
    def has_access(self, user_id):
        """Check if user has access"""
        user_id = str(user_id)
        return self.data['users'].get(user_id, {}).get('has_access', False)
    
    def get_user(self, user_id):
        """Get user data"""
        user_id = str(user_id)
        return self.data['users'].get(user_id)
    
    def add_pending_link(self, user_id, username, link_type, description):
        """Add pending link request"""
        request = {
            'id': len(self.data['pending_links']) + 1,
            'user_id': user_id,
            'username': username,
            'link_type': link_type,
            'description': description,
            'requested_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        self.data['pending_links'].append(request)
        self.save_data()
        return request['id']
    
    def get_pending_links(self):
        """Get all pending link requests"""
        return [req for req in self.data['pending_links'] if req['status'] == 'pending']
    
    def approve_link(self, request_id, admin_id, private_link):
        """Approve a link request"""
        for req in self.data['pending_links']:
            if req['id'] == request_id and req['status'] == 'pending':
                req['status'] = 'approved'
                req['approved_by'] = admin_id
                req['approved_at'] = datetime.now().isoformat()
                req['private_link'] = private_link
                
                # Move to approved links
                self.data['approved_links'].append(req.copy())
                self.save_data()
                return True
        return False
    
    def reject_link(self, request_id, admin_id, reason=None):
        """Reject a link request"""
        for req in self.data['pending_links']:
            if req['id'] == request_id and req['status'] == 'pending':
                req['status'] = 'rejected'
                req['rejected_by'] = admin_id
                req['rejected_at'] = datetime.now().isoformat()
                if reason:
                    req['rejection_reason'] = reason
                self.save_data()
                return True
        return False

# Global database instance
db = Database()

