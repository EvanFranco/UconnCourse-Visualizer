import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urljoin, urlparse

def scrape_undergraduate_majors():
    """
    Scrapes the UConn academic catalog to extract all undergraduate majors.
    Returns a list of dictionaries containing major information.
    """
    base_url = "https://catalog.uconn.edu"
    programs_url = f"{base_url}/undergraduate/programs/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Fetch the undergraduate programs page
        print("Fetching undergraduate programs page...")
        response = requests.get(programs_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        majors = []
        seen_majors = set()
        
        # Valid undergraduate degree codes
        valid_degree_codes = {'BS', 'BA', 'BSE', 'BFA', 'BM', 'BSW', 'BGS', 'AAS', 'IB/M', 'CEIN/BS'}
        # Pattern to match major names with degree codes like "Major Name (BS)" or "Major Name (BA or BS)"
        major_name_pattern = re.compile(r'^(.+?)\s*\(([A-Z/]+(?:\s+or\s+[A-Z/]+)?)\)$')
        
        # Find all links on the page
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '').strip()
            text = link.get_text(strip=True)
            
            # Skip empty or very short text
            if not text or len(text) < 3:
                continue
            
            # Check if the link text matches a major pattern
            match = major_name_pattern.match(text)
            if not match:
                continue
            
            major_name = match.group(1).strip()
            degree_code = match.group(2).strip()
            
            # Check if it's a valid undergraduate degree code
            # Handle cases like "BA or BS" by checking if any valid code is present
            degree_codes_in_text = re.findall(r'\b([A-Z/]+)\b', degree_code)
            is_undergrad_degree = any(
                code in valid_degree_codes or 
                code.replace('/', '') in valid_degree_codes or
                'or' in degree_code.lower()  # If it says "BA or BS", it's likely undergraduate
                for code in degree_codes_in_text
            )
            
            # Also check the URL - undergraduate program pages typically have specific patterns
            # Exclude course pages (which have /courses/ in the URL)
            # Exclude graduate programs
            is_course_page = '/courses/' in href.lower()
            is_graduate = '/graduate/' in href.lower()
            is_program_page = (
                '/undergraduate/' in href.lower() and 
                ('/programs/' in href.lower() or 
                 any(college in href.lower() for college in ['business', 'engineering', 'fine-arts', 'liberal-arts', 'agriculture', 'nursing', 'pharmacy']))
            )
            
            # Only include if it's an undergraduate program (not a course, not graduate)
            if is_undergrad_degree and not is_course_page and not is_graduate:
                # Clean up the URL
                if href.startswith('/'):
                    full_url = urljoin(base_url, href)
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(programs_url, href)
                
                # Use the full text as the name (e.g., "Accounting (BS)")
                full_major_name = text.strip()
                
                if full_major_name not in seen_majors:
                    seen_majors.add(full_major_name)
                    majors.append({
                        'name': full_major_name,
                        'url': full_url
                    })
        
        # Also look for majors in list items and paragraphs that might not be links
        # but are clearly listed as majors
        content_elements = soup.find_all(['li', 'div', 'p', 'td'])
        
        for element in content_elements:
            text = element.get_text(strip=True)
            
            # Check if it matches the major pattern
            match = major_name_pattern.match(text)
            if not match:
                continue
            
            degree_code = match.group(2).strip()
            degree_codes_in_text = re.findall(r'\b([A-Z/]+)\b', degree_code)
            is_undergrad_degree = any(
                code in valid_degree_codes or 
                code.replace('/', '') in valid_degree_codes or
                'or' in degree_code.lower()
                for code in degree_codes_in_text
            )
            
            if is_undergrad_degree and text not in seen_majors:
                # Try to find a link within this element
                link = element.find('a', href=True)
                if link:
                    href = link.get('href', '').strip()
                    if href.startswith('/'):
                        full_url = urljoin(base_url, href)
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        full_url = urljoin(programs_url, href)
                else:
                    # If no link, try to construct one from the major name
                    # This is a fallback - some majors might not have direct links
                    full_url = None
                
                # Only add if it's clearly an undergraduate major (not a course code)
                # Course codes are typically 4 letters like (ACCT), (AFRI), etc.
                # Degree codes are typically 2-3 letters like (BS), (BA), (BSE)
                if len(degree_code.replace(' or ', '').replace('/', '')) <= 5:  # Degree codes are short
                    seen_majors.add(text)
                    majors.append({
                        'name': text,
                        'url': full_url
                    })
        
        # Remove duplicates and sort
        unique_majors = {}
        for major in majors:
            name = major['name']
            if name not in unique_majors:
                unique_majors[name] = major
            elif major['url'] and not unique_majors[name]['url']:
                # Prefer entries with URLs
                unique_majors[name] = major
        
        majors = list(unique_majors.values())
        majors.sort(key=lambda x: x['name'])
        
        print(f"\nFound {len(majors)} undergraduate majors")
        return majors
        
    except requests.RequestException as e:
        print(f"Error fetching the catalog: {e}")
        return []
    except Exception as e:
        print(f"Error parsing the catalog: {e}")
        import traceback
        traceback.print_exc()
        return []


def save_majors_to_json(majors, filename='undergraduate_majors.json'):
    """Save the scraped majors to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(majors, f, indent=2, ensure_ascii=False)
    print(f"\nMajors saved to {filename}")


def scrape_major_requirements(major_url, headers):
    """
    Scrapes the requirements page for a specific major.
    Returns a dictionary with requirements information.
    """
    try:
        response = requests.get(major_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        requirements = {
            'total_credits': None,
            'required_courses': [],
            'elective_courses': [],
            'course_groups': [],  # Groups of courses where you need to pick one or more
            'requirements_text': [],
            'additional_requirements': []
        }
        
        # Find the main content area
        # Requirements are typically in sections with headings like "Requirements", "Course Requirements", etc.
        content = soup.find('main') or soup.find('div', class_=re.compile(r'content|main|program', re.I)) or soup
        
        # Look for requirement sections
        requirement_sections = content.find_all(['section', 'div'], 
                                               class_=lambda x: x and any(
                                                   keyword in str(x).lower() 
                                                   for keyword in ['requirement', 'course', 'curriculum', 'program']
                                               ))
        
        # Also look for headings that indicate requirements
        headings = content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        for heading in headings:
            heading_text = heading.get_text(strip=True).lower()
            if any(keyword in heading_text for keyword in ['requirement', 'course', 'curriculum', 'program', 'credit']):
                # Get the content after this heading
                section_content = []
                next_sibling = heading.find_next_sibling()
                
                # Collect content until next heading of same or higher level
                heading_level = int(heading.name[1]) if heading.name.startswith('h') else 6
                
                while next_sibling:
                    if next_sibling.name and next_sibling.name.startswith('h'):
                        next_level = int(next_sibling.name[1])
                        if next_level <= heading_level:
                            break
                    
                    section_content.append(next_sibling)
                    next_sibling = next_sibling.find_next_sibling()
                
                # Extract text from this section
                section_text = ' '.join([elem.get_text(separator=' ', strip=True) for elem in section_content if elem])
                if section_text:
                    requirements['requirements_text'].append({
                        'heading': heading.get_text(strip=True),
                        'content': section_text
                    })
        
        # Look for course codes in the format: DEPT 1234 or DEPT 1234Q
        course_pattern = re.compile(r'\b([A-Z]{2,5})\s+(\d{4}[A-Z]?)\b')
        
        # Extract all course codes from the page
        page_text = content.get_text()
        found_courses = course_pattern.findall(page_text)
        
        # Deduplicate courses
        unique_courses = set()
        for dept, num in found_courses:
            course_code = f"{dept} {num}"
            unique_courses.add(course_code)
        
        requirements['required_courses'] = sorted(list(unique_courses))
        
        # Look for credit requirements
        credit_patterns = [
            re.compile(r'(\d+)\s+credits?', re.I),
            re.compile(r'total\s+of\s+(\d+)\s+credits?', re.I),
            re.compile(r'minimum\s+of\s+(\d+)\s+credits?', re.I),
        ]
        
        for pattern in credit_patterns:
            matches = pattern.findall(page_text)
            if matches:
                # Take the largest number as total credits
                credit_numbers = [int(m) for m in matches if int(m) > 0 and int(m) < 200]
                if credit_numbers:
                    requirements['total_credits'] = max(credit_numbers)
                    break
        
        # Look for lists of courses (often in <ul> or <ol> tags)
        lists = content.find_all(['ul', 'ol'])
        for list_elem in lists:
            list_items = list_elem.find_all('li', recursive=False)
            if list_items:
                # Check if this looks like a course list
                item_texts = [li.get_text(strip=True) for li in list_items]
                courses_in_list = []
                
                for item_text in item_texts:
                    # Check if item contains course codes
                    course_matches = course_pattern.findall(item_text)
                    if course_matches:
                        for dept, num in course_matches:
                            courses_in_list.append(f"{dept} {num}")
                
                if courses_in_list:
                    # Check if it's a choice group (contains "or", "select", "choose")
                    list_text = ' '.join(item_texts).lower()
                    is_choice = any(word in list_text for word in ['or', 'select', 'choose', 'one of', 'either'])
                    
                    if is_choice:
                        requirements['course_groups'].append({
                            'type': 'choice',
                            'courses': sorted(list(set(courses_in_list))),
                            'description': ' '.join(item_texts[:3])  # First few items as description
                        })
                    else:
                        # Might be required courses
                        requirements['required_courses'].extend(courses_in_list)
        
        # Remove duplicates from required courses
        requirements['required_courses'] = sorted(list(set(requirements['required_courses'])))
        
        return requirements
        
    except requests.RequestException as e:
        print(f"  Error fetching requirements: {e}")
        return None
    except Exception as e:
        print(f"  Error parsing requirements: {e}")
        return None


def scrape_all_major_requirements(majors, delay=1):
    """
    Scrapes requirements for all majors.
    delay: seconds to wait between requests to be respectful to the server
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    majors_with_requirements = []
    total = len(majors)
    
    print(f"\nScraping requirements for {total} majors...")
    print("This may take a while. Please be patient.\n")
    
    for i, major in enumerate(majors, 1):
        major_name = major.get('name', 'Unknown')
        major_url = major.get('url')
        
        if not major_url:
            print(f"[{i}/{total}] Skipping {major_name} - no URL")
            majors_with_requirements.append({
                **major,
                'requirements': None,
                'error': 'No URL provided'
            })
            continue
        
        print(f"[{i}/{total}] Scraping {major_name}...", end=' ', flush=True)
        
        requirements = scrape_major_requirements(major_url, headers)
        
        if requirements:
            majors_with_requirements.append({
                **major,
                'requirements': requirements
            })
            print(f"✓ Found {len(requirements['required_courses'])} courses")
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
    
    return majors_with_requirements


def print_majors(majors):
    """Print the list of majors in a readable format."""
    print("\n" + "="*60)
    print("UNDERGRADUATE MAJORS AT UCONN")
    print("="*60)
    for i, major in enumerate(majors, 1):
        print(f"{i:3d}. {major['name']}")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    print("UConn Undergraduate Majors Scraper")
    print("-" * 60)
    
    # Check if we should scrape requirements
    scrape_reqs = '--requirements' in sys.argv or '-r' in sys.argv
    
    # Check if we should load existing majors
    load_existing = '--load' in sys.argv or '-l' in sys.argv
    
    if load_existing:
        # Load existing majors from JSON
        try:
            with open('undergraduate_majors.json', 'r', encoding='utf-8') as f:
                all_majors = json.load(f)
            
            # Filter out invalid entries (those without proper URLs or with malformed names)
            majors = []
            for major in all_majors:
                name = major.get('name', '')
                url = major.get('url', '')
                
                # Skip entries that look malformed (very long names, no proper URL structure)
                if (url and 
                    url.startswith('http') and 
                    len(name) < 200 and  # Reasonable name length
                    not name.startswith('#') and  # Skip navigation entries
                    '/undergraduate/' in url):  # Must be undergraduate program
                    majors.append(major)
            
            print(f"Loaded {len(majors)} valid majors from undergraduate_majors.json (filtered from {len(all_majors)} total)")
        except FileNotFoundError:
            print("No existing majors file found. Scraping majors first...")
            majors = scrape_undergraduate_majors()
            if majors:
                save_majors_to_json(majors)
    else:
        majors = scrape_undergraduate_majors()
        if majors:
            save_majors_to_json(majors)
    
    if not majors:
        print("No majors found. The website structure may have changed.")
        sys.exit(1)
    
    if scrape_reqs:
        # Scrape requirements for all majors
        majors_with_requirements = scrape_all_major_requirements(majors, delay=1)
        
        # Save to a new file
        output_file = 'undergraduate_majors_with_requirements.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(majors_with_requirements, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved {len(majors_with_requirements)} majors with requirements to {output_file}")
        
        # Print summary
        successful = sum(1 for m in majors_with_requirements if m.get('requirements') is not None)
        print(f"\nSummary: {successful}/{len(majors_with_requirements)} majors successfully scraped")
    else:
        print_majors(majors)
        print("\nTo scrape requirements, run with --requirements or -r flag:")
        print("  python python_scraper/coruse.py --requirements")
        print("\nOr to load existing majors and scrape requirements:")
        print("  python python_scraper/coruse.py --load --requirements")

