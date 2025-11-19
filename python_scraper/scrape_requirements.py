import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urljoin, urlparse

def scrape_major_requirements_from_section(major_url, headers):
    """
    Scrapes the requirements from the #requirementstext section of a major's page.
    Returns a dictionary with structured requirements information.
    """
    # Add the #requirementstext anchor to the URL
    requirements_url = major_url
    if '#requirementstext' not in requirements_url:
        requirements_url = requirements_url.rstrip('/') + '#requirementstext'
    
    try:
        response = requests.get(requirements_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        requirements = {
            'total_credits': None,
            'required_courses': [],
            'course_requirements': [],  # Structured requirements with groups
            'elective_requirements': [],
            'requirements_text': '',
            'raw_html': None
        }
        
        # Find the requirements section by ID or by finding the anchor target
        requirements_section = None
        
        # Try to find by ID first
        requirements_section = soup.find(id='requirementstext')
        
        # If not found, try to find by name attribute
        if not requirements_section:
            requirements_section = soup.find('a', {'name': 'requirementstext'})
            if requirements_section:
                # Get the parent section
                requirements_section = requirements_section.find_parent(['section', 'div'])
        
        # If still not found, look for headings containing "Requirements"
        if not requirements_section:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'], string=re.compile(r'requirement', re.I))
            if headings:
                requirements_section = headings[0].find_next_sibling(['div', 'section'])
                if not requirements_section:
                    # Try to get all content after the heading
                    requirements_section = headings[0].parent
        
        # Fallback: use main content area
        if not requirements_section:
            requirements_section = soup.find('main') or soup.find('div', class_=re.compile(r'content|main', re.I)) or soup
        
        if requirements_section:
            # Extract the text content
            requirements['requirements_text'] = requirements_section.get_text(separator='\n', strip=True)
            requirements['raw_html'] = str(requirements_section)
        
        # Parse structured requirements from the section
        if requirements_section:
            # Look for tables (requirements are often in tables)
            tables = requirements_section.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                current_group = None
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        # First cell usually has course info, second has credits
                        first_cell = cells[0].get_text(strip=True)
                        second_cell = cells[1].get_text(strip=True) if len(cells) > 1 else ''
                        
                        # Check if this is a group header (like "Select one of the following:")
                        if any(keyword in first_cell.lower() for keyword in ['select', 'choose', 'one of', 'either', 'or']):
                            # This might be a choice group
                            current_group = {
                                'type': 'choice',
                                'description': first_cell,
                                'courses': [],
                                'credits': None
                            }
                            
                            # Try to extract credit amount
                            credit_match = re.search(r'(\d+)', second_cell)
                            if credit_match:
                                current_group['credits'] = int(credit_match.group(1))
                        else:
                            # Look for course codes in the first cell
                            course_pattern = re.compile(r'\b([A-Z]{2,5}(?:/[A-Z]{2,5})*)\s+(\d{4}[A-Z]?)\b')
                            course_matches = course_pattern.findall(first_cell)
                            
                            if course_matches:
                                for dept, num in course_matches:
                                    course_code = f"{dept} {num}"
                                    
                                    if current_group:
                                        current_group['courses'].append(course_code)
                                    else:
                                        # Direct required course
                                        requirements['required_courses'].append(course_code)
                            
                            # Check if this row indicates a group is complete
                            if 'total' in first_cell.lower() or 'credits' in first_cell.lower():
                                if current_group and current_group['courses']:
                                    requirements['course_requirements'].append(current_group)
                                current_group = None
            
            # Also look for lists (ul/ol) that contain course requirements
            lists = requirements_section.find_all(['ul', 'ol'])
            for list_elem in lists:
                list_items = list_elem.find_all('li', recursive=False)
                parent_text = ''
                
                # Check parent for context (might be a heading or paragraph before the list)
                parent = list_elem.find_parent(['div', 'section', 'p'])
                if parent:
                    # Look for heading or text before the list
                    prev_siblings = []
                    for sibling in list_elem.previous_siblings:
                        if hasattr(sibling, 'get_text'):
                            text = sibling.get_text(strip=True)
                            if text:
                                prev_siblings.append(text)
                    parent_text = ' '.join(prev_siblings[:2])
                
                # Determine if this is a choice group
                is_choice = any(keyword in parent_text.lower() for keyword in ['select', 'choose', 'one of', 'either', 'or'])
                
                courses_in_list = []
                for item in list_items:
                    item_text = item.get_text(strip=True)
                    course_pattern = re.compile(r'\b([A-Z]{2,5}(?:/[A-Z]{2,5})*)\s+(\d{4}[A-Z]?)\b')
                    course_matches = course_pattern.findall(item_text)
                    
                    for dept, num in course_matches:
                        courses_in_list.append(f"{dept} {num}")
                
                if courses_in_list:
                    if is_choice:
                        requirements['course_requirements'].append({
                            'type': 'choice',
                            'description': parent_text or 'Select from the following',
                            'courses': sorted(list(set(courses_in_list))),
                            'credits': None
                        })
                    else:
                        # Add to required courses
                        requirements['required_courses'].extend(courses_in_list)
            
            # Extract all course codes from the entire section
            section_text = requirements_section.get_text()
            course_pattern = re.compile(r'\b([A-Z]{2,5}(?:/[A-Z]{2,5})*)\s+(\d{4}[A-Z]?)\b')
            all_courses = course_pattern.findall(section_text)
            
            # Add any courses we might have missed
            for dept, num in all_courses:
                course_code = f"{dept} {num}"
                if course_code not in requirements['required_courses']:
                    # Check if it's already in a requirement group
                    in_group = False
                    for req_group in requirements['course_requirements']:
                        if course_code in req_group.get('courses', []):
                            in_group = True
                            break
                    if not in_group:
                        requirements['required_courses'].append(course_code)
            
            # Remove duplicates and sort
            requirements['required_courses'] = sorted(list(set(requirements['required_courses'])))
            
            # Look for total credit requirements
            credit_patterns = [
                re.compile(r'total\s+credits?:?\s*(\d+)', re.I),
                re.compile(r'(\d+)\s+total\s+credits?', re.I),
                re.compile(r'minimum\s+of\s+(\d+)\s+credits?', re.I),
            ]
            
            for pattern in credit_patterns:
                matches = pattern.findall(section_text)
                if matches:
                    credit_numbers = [int(m) for m in matches if 0 < int(m) < 200]
                    if credit_numbers:
                        requirements['total_credits'] = max(credit_numbers)
                        break
            
            # Look for "Total Credits" in tables
            if not requirements['total_credits']:
                total_rows = requirements_section.find_all('tr')
                for row in total_rows:
                    row_text = row.get_text(strip=True)
                    if 'total' in row_text.lower() and 'credit' in row_text.lower():
                        credit_match = re.search(r'(\d+)', row_text)
                        if credit_match:
                            requirements['total_credits'] = int(credit_match.group(1))
                            break
        
        return requirements
        
    except requests.RequestException as e:
        print(f"  Error fetching requirements: {e}")
        return None
    except Exception as e:
        print(f"  Error parsing requirements: {e}")
        import traceback
        traceback.print_exc()
        return None


def scrape_all_requirements(input_file='undergraduate_majors.json', output_file='undergraduate_majors_with_requirements.json', delay=1):
    """
    Loads majors from JSON file and scrapes requirements for each.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Load majors from file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            all_majors = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Please run the main scraper first.")
        return
    
    # Filter out invalid entries
    majors = []
    for major in all_majors:
        name = major.get('name', '')
        url = major.get('url', '')
        
        if (url and 
            url.startswith('http') and 
            len(name) < 200 and
            not name.startswith('#') and
            '/undergraduate/' in url):
            majors.append(major)
    
    print(f"Loaded {len(majors)} valid majors from {input_file}")
    print(f"Scraping requirements from #requirementstext sections...")
    print("This may take a while. Please be patient.\n")
    
    majors_with_requirements = []
    total = len(majors)
    
    for i, major in enumerate(majors, 1):
        major_name = major.get('name', 'Unknown')
        major_url = major.get('url')
        
        print(f"[{i}/{total}] Scraping {major_name}...", end=' ', flush=True)
        
        requirements = scrape_major_requirements_from_section(major_url, headers)
        
        if requirements:
            majors_with_requirements.append({
                **major,
                'requirements': requirements
            })
            course_count = len(requirements.get('required_courses', []))
            group_count = len(requirements.get('course_requirements', []))
            print(f"✓ Found {course_count} courses, {group_count} requirement groups")
        else:
            majors_with_requirements.append({
                **major,
                'requirements': None,
                'error': 'Failed to scrape requirements'
            })
            print("✗ Failed")
        
        # Be respectful - wait between requests
        if i < total:
            time.sleep(delay)
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(majors_with_requirements, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved {len(majors_with_requirements)} majors with requirements to {output_file}")
    
    # Print summary
    successful = sum(1 for m in majors_with_requirements if m.get('requirements') is not None)
    print(f"\nSummary: {successful}/{len(majors_with_requirements)} majors successfully scraped")
    
    # Print some statistics
    if successful > 0:
        total_courses = sum(len(m.get('requirements', {}).get('required_courses', [])) for m in majors_with_requirements if m.get('requirements'))
        total_groups = sum(len(m.get('requirements', {}).get('course_requirements', [])) for m in majors_with_requirements if m.get('requirements'))
        print(f"Total courses found: {total_courses}")
        print(f"Total requirement groups found: {total_groups}")


if __name__ == "__main__":
    import sys
    
    # Allow custom input/output files via command line
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'undergraduate_majors.json'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'undergraduate_majors_with_requirements.json'
    delay = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    
    print("UConn Major Requirements Scraper")
    print("=" * 60)
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Delay between requests: {delay} seconds")
    print("=" * 60)
    print()
    
    scrape_all_requirements(input_file, output_file, delay)

