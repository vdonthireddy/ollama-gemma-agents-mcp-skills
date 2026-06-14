import os
import json
import unittest

class TestSkills(unittest.TestCase):
    def check_skills_in_dir(self, dir_name):
        skills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), dir_name)
        self.assertTrue(os.path.exists(skills_dir), f"{dir_name} directory does not exist")
        
        files = [f for f in os.listdir(skills_dir) if f.endswith(".json")]
        self.assertEqual(len(files), 3, f"Expected 3 skill files in {dir_name}, found {len(files)}")
        
        for file in files:
            filepath = os.path.join(skills_dir, file)
            with open(filepath, "r") as f:
                data = json.load(f)
                
            self.assertIn("id", data, f"Missing 'id' in {file}")
            self.assertIn("name", data, f"Missing 'name' in {file}")
            self.assertIn("description", data, f"Missing 'description' in {file}")
            self.assertIn("sequence", data, f"Missing 'sequence' in {file}")
            self.assertIn("instructions", data, f"Missing 'instructions' in {file}")
            
            self.assertTrue(isinstance(data["sequence"], list), f"'sequence' in {file} should be a list")
            self.assertTrue(len(data["sequence"]) >= 3, f"'sequence' in {file} should have at least 3 tools")

    def test_travel_skills(self):
        import os
        self.check_skills_in_dir(os.path.join("mcp_servers", "travel", "skills"))

    def test_party_skills(self):
        import os
        self.check_skills_in_dir(os.path.join("mcp_servers", "party", "skills"))

if __name__ == "__main__":
    unittest.main()
