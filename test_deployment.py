import os
import unittest
import json
import sys

class DeploymentReadinessTest(unittest.TestCase):
    """Test case for checking deployment readiness without relying on Django"""
    
    def setUp(self):
        """Set up test data"""
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
    
    def test_required_files_exist(self):
        """Test that required files for deployment exist"""
        # Check that Procfile exists
        self.assertTrue(os.path.exists(os.path.join(self.base_dir, 'Procfile')))
        
        # Check that requirements.txt exists
        self.assertTrue(os.path.exists(os.path.join(self.base_dir, 'requirements.txt')))
        
        # Check that .gitignore exists
        self.assertTrue(os.path.exists(os.path.join(self.base_dir, '.gitignore')))
        
        # Check that manage.py exists
        self.assertTrue(os.path.exists(os.path.join(self.base_dir, 'manage.py')))
        
        # Check that wsgi.py exists
        self.assertTrue(os.path.exists(os.path.join(self.base_dir, 'project', 'wsgi.py')))
    
    def test_procfile_content(self):
        """Test that Procfile has the correct content"""
        with open(os.path.join(self.base_dir, 'Procfile'), 'r') as f:
            content = f.read().strip()
            self.assertEqual(content, 'web: gunicorn project.wsgi:application')
    
    def test_requirements_content(self):
        """Test that requirements.txt has the necessary packages"""
        with open(os.path.join(self.base_dir, 'requirements.txt'), 'r') as f:
            content = f.read()
            
            # Check for Django
            self.assertIn('django', content.lower())
            
            # Check for gunicorn
            self.assertIn('gunicorn', content.lower())
            
            # Check for psycopg2 or psycopg2-binary
            self.assertTrue('psycopg2' in content.lower() or 'psycopg2-binary' in content.lower())
            
            # Check for dj-database-url
            self.assertIn('dj-database-url', content.lower())
            
            # Check for stripe
            self.assertIn('stripe', content.lower())
    
    def test_docker_compose_file(self):
        """Test that docker-compose.yml exists and has the necessary services"""
        docker_compose_path = os.path.join(self.base_dir, 'docker-compose.yml')
        
        # Check that docker-compose.yml exists
        self.assertTrue(os.path.exists(docker_compose_path))
        
        # Check that docker-compose.yml has the necessary services
        with open(docker_compose_path, 'r') as f:
            content = f.read().lower()
            
            # Check for web service
            self.assertIn('web:', content)
            
            # Check for db service
            self.assertIn('db:', content)
            
            # Check for nginx service
            self.assertIn('nginx:', content)
    
    def test_dockerfile(self):
        """Test that Dockerfile exists and has the necessary commands"""
        dockerfile_path = os.path.join(self.base_dir, 'Dockerfile')
        
        # Check that Dockerfile exists
        self.assertTrue(os.path.exists(dockerfile_path))
        
        # Check that Dockerfile has the necessary commands
        with open(dockerfile_path, 'r') as f:
            content = f.read().lower()
            
            # Check for FROM command
            self.assertIn('from', content)
            
            # Check for WORKDIR command
            self.assertIn('workdir', content)
            
            # Check for COPY command
            self.assertIn('copy', content)
            
            # Check for RUN command
            self.assertIn('run', content)
            
            # Check for CMD command
            self.assertIn('cmd', content)
    
    def test_github_workflow(self):
        """Test that GitHub workflow file exists and has the necessary jobs"""
        workflow_path = os.path.join(self.base_dir, '.github', 'workflows', 'django-ci.yml')
        
        # Check that GitHub workflow file exists
        self.assertTrue(os.path.exists(workflow_path))
        
        # Check that GitHub workflow file has the necessary jobs
        with open(workflow_path, 'r') as f:
            content = f.read().lower()
            
            # Check for test job
            self.assertIn('test:', content)
            
            # Check for deploy job
            self.assertIn('deploy:', content)

if __name__ == '__main__':
    unittest.main()
