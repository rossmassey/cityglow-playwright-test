# booking.py
from playwright.sync_api import sync_playwright

# Global variable to store startup data
startup_data = None

HEADLESS_MODE=False # show a debug browser or not
DEBUG_BROWSER_WIDTH=1200
DEBUG_BROWSER_HEIGHT=800
SHOW_DEV_TOOLS=False

SLOW_MO_DELAY=1000 # ms to wait each step
PAUSE_MODE=True # pause at start and end

def setup_browser_and_page():
    """Initialize browser and page with response interception"""
    global startup_data
    
    browser = playwright.chromium.launch(headless=HEADLESS_MODE, slow_mo=SLOW_MO_DELAY, devtools=SHOW_DEV_TOOLS)
    context = browser.new_context(viewport={"width":DEBUG_BROWSER_WIDTH, "height":DEBUG_BROWSER_HEIGHT})
    page = context.new_page()
    
    # Intercept startup JSON
    def on_response(response):
        global startup_data
        if "booking/app/startup" in response.url:
            startup_data = response.json()
    
    page.on("response", on_response)
    
    return browser, page

def print_service_categories():
    """Print all available service categories"""
    if startup_data:
        categories = startup_data['servicesInfo']['serviceCategories']
        print(f"\n📂 All Service Categories ({len(categories)} total):")
        for category in categories:
            print(f"  {category['id']}: {category['name']}")

def print_services(service_category):
    """Print all services within a specific category"""
    if not startup_data:
        return
        
    categories = startup_data['servicesInfo']['serviceCategories']
    services = startup_data['servicesInfo']['servicesById']
    
    # Find category ID
    category_id = None
    for category in categories:
        if category['name'] == service_category:
            category_id = category['id']
            break
    
    # Print filtered services
    if category_id:
        filtered_services = {sid: sinfo for sid, sinfo in services.items() 
                           if sinfo['serviceCategoryId'] == category_id}
        print(f"\n📋 Available {service_category} services ({len(filtered_services)} total):")
        for service_id, service_info in filtered_services.items():
            print(f"  {service_id}: {service_info['name']} - ${service_info['defaultPrice']}")

def print_addons(sub_service):
    """Print available add-ons for a specific service"""
    if not startup_data:
        return
        
    services = startup_data['servicesInfo']['servicesById']
    
    # Find service ID
    selected_service_id = None
    for service_id, service_info in services.items():
        if service_info['name'] == sub_service:
            selected_service_id = service_id
            break
    
    print(f"Selected service ID for '{sub_service}': {selected_service_id}")
    
    # Print add-ons
    if selected_service_id:
        option_group_ids = startup_data['servicesInfo'].get('serviceOptionGroupIdsByServiceId', {}).get(selected_service_id, [])
        print(f"Option group IDs for service {selected_service_id}: {option_group_ids}")
        
        if option_group_ids:
            option_groups = startup_data['servicesInfo']['serviceOptionGroupsById']
            service_options = startup_data['servicesInfo']['serviceOptionsById']
            
            print(f"\n🔧 Available add-ons for {sub_service}:")
            for group_id in option_group_ids:
                group = option_groups[str(group_id)]
                print(f"  Group {group['name']}: {group['prompt']}")
                
                # Find options in this group
                group_options = {opt_id: opt for opt_id, opt in service_options.items() 
                               if opt['serviceOptionGroupId'] == group_id}
                for opt_id, option in group_options.items():
                    print(f"    {opt_id}: {option['name']} - ${option['price']}")

def print_staff(sub_service):
    """Print available staff for a specific service"""
    if not startup_data:
        return
        
    services = startup_data['servicesInfo']['servicesById']
    staff_by_id = startup_data['staffInfo']['staffById']
    staff_ids_by_service = startup_data['staffInfo']['staffIdsByServiceId']
    
    # Find service ID
    selected_service_id = None
    for service_id, service_info in services.items():
        if service_info['name'] == sub_service:
            selected_service_id = service_id
            break
    
    # Print available staff
    if selected_service_id and selected_service_id in staff_ids_by_service:
        available_staff_ids = staff_ids_by_service[selected_service_id]
        print(f"\n👥 Available staff for {sub_service} ({len(available_staff_ids)} total):")
        
        for staff_id in available_staff_ids:
            staff = staff_by_id[str(staff_id)]
            full_name = staff['firstName']
            if staff['lastName']:
                full_name += f" {staff['lastName']}"
            print(f"  {staff_id}: {full_name}")


def open_page_and_booking(page):
    """Navigate to the booking page and open iframe"""
    page.goto("https://www.cityglowflorida.com/")
    
    # Click BOOK ONLINE
    link = page.get_by_role("link", name="BOOK ONLINE")
    link.wait_for(state="visible")
    link.click()
    
    # Get iframe content
    iframe_content = page.locator('iframe[title="Mangomint Online Booking"]').content_frame
    page.wait_for_timeout(3000)  # Wait for data to load
    
    return iframe_content

def select_service_category(iframe_content, service_category):
    """Click on the service category"""
    iframe_content.get_by_text(service_category).wait_for(state="visible")
    iframe_content.get_by_text(service_category).click()

def select_sub_service(iframe_content, sub_service):
    """Click on the specific sub-service"""
    iframe_content.get_by_text(sub_service).wait_for(state="visible")
    iframe_content.get_by_text(sub_service).click()

def select_addons(iframe_content, page, addons):
    """Select add-ons if provided, otherwise click Continue"""
    if not addons:
        # No addons, just click Continue
        iframe_content.get_by_role("button", name="Continue").wait_for(state="visible")
        iframe_content.get_by_role("button", name="Continue").click()
        return
    
    # Select each addon
    for addon in addons:
        print(f"Selecting addon: {addon}")
        iframe_content.get_by_text(addon).wait_for(state="visible")
        iframe_content.get_by_text(addon).click(force=True)
    
    # Wait a moment for selections to register
    page.wait_for_timeout(1000)
    
    # Click Continue after selecting addons
    iframe_content.get_by_role("button", name="Continue").wait_for(state="visible")
    iframe_content.get_by_role("button", name="Continue").click()

def select_staff(iframe_content, staff):
    """Select staff member or 'Anyone' if none specified"""
    if staff:
        print(f"Selecting staff: {staff}")
        iframe_content.get_by_text(staff).wait_for(state="visible")
        iframe_content.get_by_text(staff).click()
    else:
        print("Selecting: Anyone")
        iframe_content.get_by_text("Anyone").wait_for(state="visible")
        iframe_content.get_by_text("Anyone").click()
    
    # Click No button that pops up
    iframe_content.get_by_role("button", name="No").wait_for(state="visible")
    iframe_content.get_by_role("button", name="No").click()

def select_datetime(iframe_content, page, day, month, year, time):
    """Select date and time for appointment"""
    # Convert month number to name
    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    target_month = month_names[month - 1]
    target_year = str(year)
    
    print(f"Selecting date: {target_month} {day}, {year} at {time}")
    
    # Step 1: Navigate to correct month/year
    max_attempts = 24  # Don't click forever
    for attempt in range(max_attempts):
        # Check current month/year display
        month_year_text = iframe_content.get_by_text(f"{target_month} {target_year}").first
        try:
            month_year_text.wait_for(state="visible", timeout=1000)
            print(f"Found target month/year: {target_month} {target_year}")
            break
        except:
            # Also check for month range format like "July / August 2025"
            try:
                month_range_locator = iframe_content.locator(f"text*={target_month}").and_(iframe_content.locator(f"text*={target_year}"))
                month_range_locator.first.wait_for(state="visible", timeout=1000)
                print(f"Found target month/year in range format")
                break
            except:
                # Click next button to navigate
                print(f"Attempt {attempt + 1}: Clicking next to find {target_month} {target_year}")
                next_button = iframe_content.locator(".DateStrip_navButton__Zoc7Z.undefined")
                next_button.wait_for(state="visible")
                next_button.click()
                page.wait_for_timeout(500)
    
    # Step 2: Navigate to correct day
    print(f"Looking for day {day}")
    max_day_attempts = 14  # Don't click forever
    for attempt in range(max_day_attempts):
        try:
            # Look for the day number
            day_locator = iframe_content.locator(".DateStrip_dayCtDate__u1AKh").filter(has_text=str(day))
            day_locator.first.wait_for(state="visible", timeout=1000)
            print(f"Found day {day}, clicking it")
            day_locator.first.click()
            break
        except:
            print(f"Day attempt {attempt + 1}: Day {day} not visible, clicking next")
            next_button = iframe_content.locator(".DateStrip_navButton__Zoc7Z.undefined")
            next_button.wait_for(state="visible")
            next_button.click()
            page.wait_for_timeout(500)
    
    # Step 3: Determine and select time period
    # Parse time to determine period (morning/afternoon/evening)
    time_lower = time.lower()
    hour = int(time.split(':')[0])
    is_pm = 'pm' in time_lower
    
    if is_pm and hour >= 5:
        period = "Evening"
        print(f"Selecting Evening period for {time}")
        evening_locator = iframe_content.get_by_text("Evening:", exact=False)
        evening_locator.wait_for(state="visible")
        evening_locator.click()
    elif (is_pm and hour >= 12) or (is_pm and hour < 5):
        period = "Afternoon" 
        print(f"Selecting Afternoon period for {time}")
        afternoon_locator = iframe_content.get_by_text("Afternoon:", exact=False)
        afternoon_locator.wait_for(state="visible")
        afternoon_locator.click()
    else:
        period = "Morning"
        print(f"Selecting Morning period for {time}")
        morning_locator = iframe_content.get_by_text("Morning:", exact=False)
        morning_locator.wait_for(state="visible") 
        morning_locator.click()
    
    # Step 4: Select specific time slot
    page.wait_for_timeout(1000)  # Wait for time slots to load
    print(f"Selecting time slot: {time}")
    try:
        time_slot = iframe_content.get_by_text(time, exact=True)
        time_slot.wait_for(state="visible", timeout=5000)
        time_slot.click()
        print(f"Successfully selected time: {time}")
    except:
        print(f"Warning: Time slot {time} not available or not found")

def fill_customer_form(iframe_content, first_name, last_name, phone, email):
    """Fill out the customer information form"""
    print(f"Filling customer form for {first_name} {last_name}")
    
    # Fill first name
    first_name_field = iframe_content.get_by_role("textbox", name="First name")
    first_name_field.wait_for(state="visible")
    first_name_field.fill(first_name)
    
    # Fill last name  
    last_name_field = iframe_content.get_by_role("textbox", name="Last name")
    last_name_field.wait_for(state="visible")
    last_name_field.fill(last_name)
    
    # Fill phone number
    phone_field = iframe_content.get_by_role("textbox", name="Phone number")
    phone_field.wait_for(state="visible")
    phone_field.fill(phone)
    
    # Fill email
    email_field = iframe_content.get_by_role("textbox", name="Email")
    email_field.wait_for(state="visible")
    email_field.fill(email)
    
    # Click cancellation agreement toggle
    cancellation_toggle = iframe_content.get_by_text("I agree to the cancellation")
    cancellation_toggle.wait_for(state="visible")
    cancellation_toggle.click()
    
    # Fill comments with "automated"
    comments_field = iframe_content.get_by_role("textbox", name="Comments")
    comments_field.wait_for(state="visible")
    comments_field.fill("automated")
    
    print("✅ Customer form completed")

def make_appointment(first_name: str, last_name: str, phone: str, email: str, service: str, sub_service: str, addons: list, staff: str, day: int, month: int, year: int, time: str):
    """
    Opens CityGlow booking page and walks through the booking flow
    """
    global playwright
    
    with sync_playwright() as p:
        global playwright
        playwright = p
        
        # Initialize browser and page
        browser, page = setup_browser_and_page()

        if PAUSE_MODE == True:
            page.pause()
        
        # Open booking page
        iframe_content = open_page_and_booking(page)
        
        # Print all categories
        print_service_categories()
        
        # Select service category
        select_service_category(iframe_content, service)
        
        # Print services in selected category
        print_services(service)
        
        # Select specific sub-service
        select_sub_service(iframe_content, sub_service)
        
        # Print add-ons for selected service
        print_addons(sub_service)
        
        # Select add-ons
        select_addons(iframe_content, page, addons)
        
        # Print available staff
        print_staff(sub_service)
        
        # Select staff
        select_staff(iframe_content, staff)
        
        # Select date and time
        select_datetime(iframe_content, page, day, month, year, time)
        
        # Fill customer form
        fill_customer_form(iframe_content, first_name, last_name, phone, email)

        if PAUSE_MODE == True:
            page.pause()
        
        # Clean up
        browser.close()

if __name__ == "__main__":
    make_appointment(
        first_name="Ross",
        last_name="Massey", 
        phone="123456",
        email="ross@ross.com",
        service="Facials",
        sub_service="HydraFacial FIRST TIME SPECIAL!",
        addons=["Extractions", "Dermaplaning"],  # or None for no addons
        staff="Elena",  # or None for "Anyone"
        day=15,
        month=8,
        year=2025,
        time="2:00 pm"
    )
