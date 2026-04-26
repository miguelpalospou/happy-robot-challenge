#!/usr/bin/env python3
"""Generate 1000 random loads for the Happy Robot demo."""

import random
from datetime import datetime, timedelta

# US Cities with state - comprehensive list
CITIES = [
    # Texas (major trucking hub)
    "Houston, TX", "Dallas, TX", "Austin, TX", "San Antonio, TX", "El Paso, TX", 
    "Fort Worth, TX", "Arlington, TX", "Corpus Christi, TX", "Plano, TX", "Laredo, TX",
    "Lubbock, TX", "Amarillo, TX", "Brownsville, TX", "McAllen, TX", "Midland, TX",
    "Odessa, TX", "Beaumont, TX", "Waco, TX", "Abilene, TX", "Tyler, TX",
    
    # California
    "Los Angeles, CA", "San Francisco, CA", "San Diego, CA", "Sacramento, CA", 
    "Fresno, CA", "Oakland, CA", "Long Beach, CA", "Bakersfield, CA", "Anaheim, CA",
    "Santa Ana, CA", "Riverside, CA", "Stockton, CA", "Irvine, CA", "Modesto, CA",
    "San Jose, CA", "San Bernardino, CA", "Ontario, CA", "Fontana, CA", "Moreno Valley, CA",
    
    # Arizona
    "Phoenix, AZ", "Tucson, AZ", "Mesa, AZ", "Scottsdale, AZ", "Chandler, AZ",
    "Gilbert, AZ", "Glendale, AZ", "Tempe, AZ", "Peoria, AZ", "Flagstaff, AZ",
    
    # Colorado
    "Denver, CO", "Colorado Springs, CO", "Aurora, CO", "Fort Collins, CO", "Pueblo, CO",
    "Boulder, CO", "Grand Junction, CO",
    
    # Illinois
    "Chicago, IL", "Springfield, IL", "Rockford, IL", "Peoria, IL", "Joliet, IL",
    "Naperville, IL", "Aurora, IL", "Elgin, IL", "Champaign, IL",
    
    # Michigan
    "Detroit, MI", "Grand Rapids, MI", "Lansing, MI", "Flint, MI", "Ann Arbor, MI",
    "Kalamazoo, MI", "Saginaw, MI", "Dearborn, MI",
    
    # Georgia
    "Atlanta, GA", "Savannah, GA", "Augusta, GA", "Columbus, GA", "Macon, GA",
    "Athens, GA", "Albany, GA", "Marietta, GA",
    
    # Florida
    "Miami, FL", "Orlando, FL", "Tampa, FL", "Jacksonville, FL", "Fort Lauderdale, FL",
    "St. Petersburg, FL", "Tallahassee, FL", "Pensacola, FL", "Fort Myers, FL",
    "West Palm Beach, FL", "Gainesville, FL", "Lakeland, FL", "Sarasota, FL",
    
    # Washington
    "Seattle, WA", "Spokane, WA", "Tacoma, WA", "Vancouver, WA", "Bellevue, WA",
    "Everett, WA", "Kent, WA", "Yakima, WA",
    
    # Oregon
    "Portland, OR", "Eugene, OR", "Salem, OR", "Bend, OR", "Medford, OR",
    
    # New York
    "New York, NY", "Buffalo, NY", "Albany, NY", "Rochester, NY", "Syracuse, NY",
    "Yonkers, NY", "Utica, NY", "Binghamton, NY",
    
    # Massachusetts
    "Boston, MA", "Worcester, MA", "Springfield, MA", "Cambridge, MA", "Lowell, MA",
    
    # Pennsylvania
    "Philadelphia, PA", "Pittsburgh, PA", "Allentown, PA", "Erie, PA", "Scranton, PA",
    "Harrisburg, PA", "Lancaster, PA", "Reading, PA",
    
    # North Carolina
    "Charlotte, NC", "Raleigh, NC", "Greensboro, NC", "Durham, NC", "Winston-Salem, NC",
    "Fayetteville, NC", "Wilmington, NC", "Asheville, NC",
    
    # Tennessee
    "Nashville, TN", "Memphis, TN", "Knoxville, TN", "Chattanooga, TN", "Clarksville, TN",
    "Murfreesboro, TN", "Jackson, TN",
    
    # Minnesota
    "Minneapolis, MN", "St. Paul, MN", "Rochester, MN", "Duluth, MN", "Bloomington, MN",
    
    # Missouri
    "Kansas City, MO", "St. Louis, MO", "Springfield, MO", "Columbia, MO", "Independence, MO",
    
    # Louisiana
    "New Orleans, LA", "Baton Rouge, LA", "Shreveport, LA", "Lafayette, LA", "Lake Charles, LA",
    
    # Oklahoma
    "Oklahoma City, OK", "Tulsa, OK", "Norman, OK", "Lawton, OK", "Broken Arrow, OK",
    
    # Nevada
    "Las Vegas, NV", "Reno, NV", "Henderson, NV", "North Las Vegas, NV", "Sparks, NV",
    
    # Utah
    "Salt Lake City, UT", "Provo, UT", "West Valley City, UT", "Ogden, UT", "St. George, UT",
    
    # New Mexico
    "Albuquerque, NM", "Santa Fe, NM", "Las Cruces, NM", "Rio Rancho, NM", "Roswell, NM",
    
    # Indiana
    "Indianapolis, IN", "Fort Wayne, IN", "Evansville, IN", "South Bend, IN", "Gary, IN",
    
    # Ohio
    "Columbus, OH", "Cleveland, OH", "Cincinnati, OH", "Toledo, OH", "Akron, OH",
    "Dayton, OH", "Youngstown, OH", "Canton, OH",
    
    # Kentucky
    "Louisville, KY", "Lexington, KY", "Bowling Green, KY", "Owensboro, KY", "Covington, KY",
    
    # Alabama
    "Birmingham, AL", "Montgomery, AL", "Mobile, AL", "Huntsville, AL", "Tuscaloosa, AL",
    
    # Arkansas
    "Little Rock, AR", "Fort Smith, AR", "Fayetteville, AR", "Springdale, AR", "Jonesboro, AR",
    
    # Nebraska
    "Omaha, NE", "Lincoln, NE", "Grand Island, NE", "Kearney, NE",
    
    # Iowa
    "Des Moines, IA", "Cedar Rapids, IA", "Davenport, IA", "Sioux City, IA", "Iowa City, IA",
    
    # Wisconsin
    "Milwaukee, WI", "Madison, WI", "Green Bay, WI", "Kenosha, WI", "Racine, WI",
    
    # Virginia
    "Richmond, VA", "Virginia Beach, VA", "Norfolk, VA", "Chesapeake, VA", "Newport News, VA",
    "Alexandria, VA", "Roanoke, VA",
    
    # Maryland
    "Baltimore, MD", "Frederick, MD", "Rockville, MD", "Gaithersburg, MD",
    
    # Washington DC
    "Washington, DC",
    
    # Connecticut
    "Hartford, CT", "New Haven, CT", "Bridgeport, CT", "Stamford, CT",
    
    # Rhode Island
    "Providence, RI", "Warwick, RI", "Cranston, RI",
    
    # New Jersey
    "Newark, NJ", "Jersey City, NJ", "Trenton, NJ", "Camden, NJ", "Paterson, NJ",
    
    # South Carolina
    "Charleston, SC", "Columbia, SC", "Greenville, SC", "Spartanburg, SC", "Myrtle Beach, SC",
    
    # Mississippi
    "Jackson, MS", "Gulfport, MS", "Biloxi, MS", "Hattiesburg, MS", "Tupelo, MS",
    
    # Kansas
    "Wichita, KS", "Kansas City, KS", "Topeka, KS", "Overland Park, KS", "Olathe, KS",
    
    # Idaho
    "Boise, ID", "Nampa, ID", "Meridian, ID", "Idaho Falls, ID", "Pocatello, ID",
    
    # Montana
    "Billings, MT", "Missoula, MT", "Great Falls, MT", "Bozeman, MT",
    
    # Wyoming
    "Cheyenne, WY", "Casper, WY", "Laramie, WY",
    
    # North Dakota
    "Fargo, ND", "Bismarck, ND", "Grand Forks, ND", "Minot, ND",
    
    # South Dakota
    "Sioux Falls, SD", "Rapid City, SD", "Aberdeen, SD",
    
    # West Virginia
    "Charleston, WV", "Huntington, WV", "Morgantown, WV",
    
    # Delaware
    "Wilmington, DE", "Dover, DE",
    
    # Maine
    "Portland, ME", "Bangor, ME", "Lewiston, ME",
    
    # New Hampshire
    "Manchester, NH", "Nashua, NH", "Concord, NH",
    
    # Vermont
    "Burlington, VT", "Montpelier, VT",
]

EQUIPMENT_TYPES = ["Dry Van", "Reefer", "Flatbed"]

COMMODITIES = {
    "Dry Van": [
        "General Merchandise", "Consumer Electronics", "Retail Goods", "Furniture", 
        "Auto Parts", "Apparel", "Office Supplies", "E-commerce Packages", 
        "Packaged Foods", "Paper Products", "Household Goods", "Toys",
        "Building Materials", "Medical Supplies", "Industrial Equipment"
    ],
    "Reefer": [
        "Fresh Produce", "Frozen Foods", "Dairy Products", "Pharmaceuticals",
        "Frozen Seafood", "Meat Products", "Beverages", "Flowers",
        "Chocolate", "Ice Cream", "Vaccines", "Fresh Flowers"
    ],
    "Flatbed": [
        "Steel Products", "Lumber", "Construction Materials", "Machinery",
        "Steel Pipes", "Concrete Products", "Heavy Equipment", "Wind Turbine Parts",
        "Steel Coils", "Prefab Buildings", "Agricultural Equipment"
    ]
}

NOTES = {
    "Dry Van": [
        "Standard freight. No special requirements.",
        "No touch freight. Seal required.",
        "Dock to dock delivery.",
        "Driver assistance required for unloading.",
        "Residential delivery. Liftgate required.",
        "High value freight. GPS tracking required.",
        "Quick turnaround needed.",
        "Same day delivery requested.",
        "Multiple stops.",
        "Time sensitive.",
    ],
    "Reefer": [
        "Temperature 34F. Food grade trailer.",
        "Temperature controlled at 35F.",
        "Frozen goods. -10F required.",
        "Temperature logs required.",
        "Climate controlled. Keep at 38F.",
        "Frozen. Maintain -20F.",
        "Fresh produce. Continuous temp monitoring.",
        "Pharmaceutical shipment. Temp validation required.",
    ],
    "Flatbed": [
        "Tarps required.",
        "Chains and straps required.",
        "Oversized permits may be needed.",
        "Straps provided.",
        "Coil racks required.",
        "Step deck preferred.",
        "Heavy haul. Check axle weights.",
    ]
}

# Approximate distances between major city pairs (simplified)
def estimate_distance(origin, dest):
    """Estimate distance based on region."""
    # Extract state from city
    origin_state = origin.split(", ")[-1]
    dest_state = dest.split(", ")[-1]
    
    # Same state = short haul
    if origin_state == dest_state:
        return random.randint(100, 400)
    
    # Regional distances
    west = ["CA", "WA", "OR", "NV", "AZ", "UT", "CO"]
    midwest = ["IL", "MI", "OH", "IN", "WI", "MN", "IA", "MO", "KS", "NE"]
    south = ["TX", "LA", "AR", "OK", "TN", "KY", "AL", "MS", "GA", "FL", "NC", "SC"]
    east = ["NY", "PA", "NJ", "MA", "CT", "RI", "MD", "VA", "DC", "DE"]
    
    def get_region(state):
        if state in west: return "west"
        if state in midwest: return "midwest"
        if state in south: return "south"
        if state in east: return "east"
        return "other"
    
    orig_region = get_region(origin_state)
    dest_region = get_region(dest_state)
    
    if orig_region == dest_region:
        return random.randint(200, 800)
    elif (orig_region == "west" and dest_region == "east") or (orig_region == "east" and dest_region == "west"):
        return random.randint(2000, 3500)
    else:
        return random.randint(600, 1800)

def calculate_rate(miles, equipment):
    """Calculate rate based on miles and equipment type."""
    # Base rate per mile varies by equipment
    if equipment == "Reefer":
        rate_per_mile = random.uniform(2.20, 3.50)
    elif equipment == "Flatbed":
        rate_per_mile = random.uniform(2.50, 4.00)
    else:  # Dry Van
        rate_per_mile = random.uniform(1.80, 3.00)
    
    base_rate = miles * rate_per_mile
    
    # Minimum rates
    if base_rate < 350:
        base_rate = random.randint(350, 500)
    
    return round(base_rate, 2)

def generate_loads(count=1000):
    """Generate load records."""
    loads = []
    
    # Date range: April 25, 2026 to May 5, 2026
    start_date = datetime(2026, 4, 25, 6, 0, 0)
    end_date = datetime(2026, 5, 5, 18, 0, 0)
    date_range_hours = int((end_date - start_date).total_seconds() / 3600)
    
    for i in range(count):
        load_id = f"LD-2026-{str(i+1).zfill(4)}"
        
        # Random origin and destination (ensure different)
        origin = random.choice(CITIES)
        destination = random.choice([c for c in CITIES if c != origin])
        
        # Random equipment type (weighted: more dry van)
        equipment = random.choices(
            EQUIPMENT_TYPES, 
            weights=[60, 25, 15]  # 60% dry van, 25% reefer, 15% flatbed
        )[0]
        
        # Random pickup time within date range
        pickup_offset = random.randint(0, date_range_hours)
        pickup_datetime = start_date + timedelta(hours=pickup_offset)
        
        # Delivery time based on distance
        miles = estimate_distance(origin, destination)
        
        # Assume 50 mph average, add loading/unloading time
        transit_hours = (miles / 50) + random.randint(2, 8)
        delivery_datetime = pickup_datetime + timedelta(hours=transit_hours)
        
        # Calculate rate
        rate = calculate_rate(miles, equipment)
        
        # Random weight based on equipment
        if equipment == "Flatbed":
            weight = random.randint(35000, 48000)
        elif equipment == "Reefer":
            weight = random.randint(28000, 42000)
        else:
            weight = random.randint(18000, 44000)
        
        # Random pieces
        pieces = random.randint(1, 100)
        
        # Commodity and notes based on equipment
        commodity = random.choice(COMMODITIES[equipment])
        notes = random.choice(NOTES[equipment])
        
        # Dimensions
        dimensions = random.choice([
            "48x40x48", "48x40x60", "48x40x40", "96x48x48", 
            "72x48x48", "36x36x36", "24x24x24", "144x96x84"
        ])
        
        load = {
            "load_id": load_id,
            "origin": origin,
            "destination": destination,
            "pickup_datetime": pickup_datetime.strftime("%Y-%m-%d %H:%M:%S-05"),
            "delivery_datetime": delivery_datetime.strftime("%Y-%m-%d %H:%M:%S-05"),
            "equipment_type": equipment,
            "loadboard_rate": rate,
            "notes": notes,
            "weight": weight,
            "commodity_type": commodity,
            "num_of_pieces": pieces,
            "miles": miles,
            "dimensions": dimensions,
            "status": "available"
        }
        loads.append(load)
    
    return loads

def generate_sql(loads):
    """Generate SQL INSERT statement."""
    sql = "-- Auto-generated loads data\n"
    sql += "-- Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    sql += f"-- Total loads: {len(loads)}\n\n"
    
    sql += "DELETE FROM negotiations;\n"
    sql += "DELETE FROM calls;\n"
    sql += "DELETE FROM loads;\n\n"
    
    sql += "INSERT INTO loads (load_id, origin, destination, pickup_datetime, delivery_datetime, equipment_type, loadboard_rate, notes, weight, commodity_type, num_of_pieces, miles, dimensions, status) VALUES\n"
    
    values = []
    for load in loads:
        val = f"('{load['load_id']}', '{load['origin']}', '{load['destination']}', '{load['pickup_datetime']}', '{load['delivery_datetime']}', '{load['equipment_type']}', {load['loadboard_rate']}, '{load['notes'].replace(chr(39), chr(39)+chr(39))}', {load['weight']}, '{load['commodity_type']}', {load['num_of_pieces']}, {load['miles']}, '{load['dimensions']}', '{load['status']}')"
        values.append(val)
    
    sql += ",\n".join(values) + ";\n"
    
    return sql

if __name__ == "__main__":
    print("Generating 1000 loads...")
    loads = generate_loads(1000)
    
    print("Writing SQL file...")
    sql = generate_sql(loads)
    
    with open("supabase/migrations/003_generated_loads.sql", "w") as f:
        f.write(sql)
    
    print("Done! Run with:")
    print("  psql <connection_string> -f supabase/migrations/003_generated_loads.sql")
    
    # Print summary
    equipment_counts = {}
    for load in loads:
        eq = load["equipment_type"]
        equipment_counts[eq] = equipment_counts.get(eq, 0) + 1
    
    print(f"\nSummary:")
    print(f"  Total loads: {len(loads)}")
    for eq, count in equipment_counts.items():
        print(f"  {eq}: {count}")
    
    rates = [l["loadboard_rate"] for l in loads]
    print(f"  Rate range: ${min(rates):.2f} - ${max(rates):.2f}")
    print(f"  Avg rate: ${sum(rates)/len(rates):.2f}")
