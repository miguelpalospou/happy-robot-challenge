-- Happy Robot - Seed Data (Expanded)
-- 40 sample loads for realistic testing

INSERT INTO loads (load_id, origin, destination, pickup_datetime, delivery_datetime, equipment_type, loadboard_rate, notes, weight, commodity_type, num_of_pieces, miles, dimensions, status) VALUES

-- TEXAS ORIGIN LOADS (popular trucking hub)
('LD-2024-001', 'Houston, TX', 'Los Angeles, CA', '2024-12-20 08:00:00-06', '2024-12-22 18:00:00-08', 'Dry Van', 3500.00, 'Dock to dock delivery. Driver assistance required.', 42000, 'Consumer Electronics', 24, 1547, '48x40x48', 'available'),
('LD-2024-002', 'Houston, TX', 'Phoenix, AZ', '2024-12-21 06:00:00-06', '2024-12-22 14:00:00-07', 'Dry Van', 2100.00, 'Residential delivery. Liftgate required.', 28000, 'Furniture', 18, 1178, '48x40x60', 'available'),
('LD-2024-003', 'Houston, TX', 'Atlanta, GA', '2024-12-20 14:00:00-06', '2024-12-21 20:00:00-05', 'Reefer', 1800.00, 'Temperature 34F. Food grade trailer.', 35000, 'Dairy Products', 40, 789, '48x40x48', 'available'),
('LD-2024-004', 'Dallas, TX', 'San Francisco, CA', '2024-12-21 06:00:00-06', '2024-12-23 20:00:00-08', 'Reefer', 4200.00, 'Temperature controlled at 35F. Produce shipment.', 38000, 'Fresh Produce', 40, 1734, '48x40x40', 'available'),
('LD-2024-005', 'Dallas, TX', 'Chicago, IL', '2024-12-22 05:00:00-06', '2024-12-23 18:00:00-06', 'Dry Van', 1900.00, 'No touch freight. Seal required.', 32000, 'Retail Goods', 50, 917, '48x40x48', 'available'),
('LD-2024-006', 'Austin, TX', 'Phoenix, AZ', '2024-12-19 14:00:00-06', '2024-12-20 16:00:00-07', 'Flatbed', 1800.00, 'Construction materials. Tarps required.', 45000, 'Building Materials', 12, 872, '96x48x48', 'available'),
('LD-2024-007', 'San Antonio, TX', 'Denver, CO', '2024-12-20 07:00:00-06', '2024-12-21 20:00:00-07', 'Dry Van', 1650.00, 'Standard freight.', 30000, 'General Merchandise', 35, 929, '48x40x48', 'available'),

-- MIDWEST ROUTES
('LD-2024-008', 'Chicago, IL', 'Denver, CO', '2024-12-20 05:00:00-06', '2024-12-21 18:00:00-07', 'Dry Van', 2200.00, 'Standard freight. No special requirements.', 35000, 'General Merchandise', 30, 1003, '48x40x48', 'available'),
('LD-2024-009', 'Chicago, IL', 'Houston, TX', '2024-12-21 08:00:00-06', '2024-12-23 16:00:00-06', 'Flatbed', 2400.00, 'Machinery. Oversized permits may be needed.', 50000, 'Industrial Equipment', 4, 1092, '144x96x84', 'available'),
('LD-2024-010', 'Chicago, IL', 'Los Angeles, CA', '2024-12-22 04:00:00-06', '2024-12-25 16:00:00-08', 'Dry Van', 4800.00, 'Team drivers preferred. High value.', 38000, 'Electronics', 25, 2015, '48x40x48', 'available'),
('LD-2024-011', 'Detroit, MI', 'Atlanta, GA', '2024-12-22 07:00:00-05', '2024-12-23 20:00:00-05', 'Dry Van', 1900.00, 'Automotive parts. Handle with care.', 28000, 'Auto Parts', 48, 721, '40x36x36', 'available'),
('LD-2024-012', 'Minneapolis, MN', 'Kansas City, MO', '2024-12-19 10:00:00-06', '2024-12-19 22:00:00-06', 'Dry Van', 850.00, 'Same day delivery requested.', 22000, 'Packaged Foods', 20, 437, '48x40x40', 'available'),
('LD-2024-013', 'Indianapolis, IN', 'Columbus, OH', '2024-12-19 13:00:00-05', '2024-12-19 17:00:00-05', 'Dry Van', 350.00, 'Quick delivery. Local run.', 18000, 'Office Supplies', 50, 176, '36x36x36', 'available'),

-- EAST COAST ROUTES
('LD-2024-014', 'New York, NY', 'Miami, FL', '2024-12-21 04:00:00-05', '2024-12-23 16:00:00-05', 'Reefer', 3100.00, 'Pharmaceutical shipment. Temperature logs required.', 18000, 'Pharmaceuticals', 16, 1280, '48x40x48', 'available'),
('LD-2024-015', 'New York, NY', 'Los Angeles, CA', '2024-12-22 04:00:00-05', '2024-12-26 20:00:00-08', 'Dry Van', 5500.00, 'High value freight. GPS tracking required.', 38000, 'Electronics', 20, 2791, '48x40x48', 'available'),
('LD-2024-016', 'New York, NY', 'Chicago, IL', '2024-12-20 06:00:00-05', '2024-12-21 14:00:00-06', 'Dry Van', 1600.00, 'Fashion merchandise. Keep dry.', 25000, 'Apparel', 60, 790, '48x40x48', 'available'),
('LD-2024-017', 'Boston, MA', 'Philadelphia, PA', '2024-12-20 12:00:00-05', '2024-12-20 20:00:00-05', 'Dry Van', 650.00, 'Quick turnaround needed.', 25000, 'Retail Goods', 35, 304, '48x40x40', 'available'),
('LD-2024-018', 'Charlotte, NC', 'Washington, DC', '2024-12-22 06:00:00-05', '2024-12-22 18:00:00-05', 'Flatbed', 1100.00, 'Steel coils. Chains and straps required.', 48000, 'Steel Products', 8, 391, '72x48x36', 'available'),
('LD-2024-019', 'Atlanta, GA', 'Jacksonville, FL', '2024-12-21 08:00:00-05', '2024-12-21 16:00:00-05', 'Dry Van', 550.00, 'Standard delivery.', 24000, 'Consumer Goods', 30, 346, '48x40x48', 'available'),

-- WEST COAST ROUTES
('LD-2024-020', 'Los Angeles, CA', 'Seattle, WA', '2024-12-21 06:00:00-08', '2024-12-23 14:00:00-08', 'Reefer', 2800.00, 'Produce. Temperature 38F.', 36000, 'Fresh Produce', 45, 1137, '48x40x48', 'available'),
('LD-2024-021', 'Los Angeles, CA', 'Las Vegas, NV', '2024-12-20 16:00:00-08', '2024-12-20 23:00:00-08', 'Dry Van', 700.00, 'Evening delivery preferred.', 30000, 'Hotel Supplies', 45, 270, '48x40x48', 'available'),
('LD-2024-022', 'Los Angeles, CA', 'Phoenix, AZ', '2024-12-22 08:00:00-08', '2024-12-22 18:00:00-07', 'Dry Van', 650.00, 'Standard freight.', 28000, 'General Merchandise', 40, 373, '48x40x48', 'available'),
('LD-2024-023', 'Seattle, WA', 'Portland, OR', '2024-12-19 09:00:00-08', '2024-12-19 14:00:00-08', 'Dry Van', 450.00, 'Short haul. Multiple stops.', 15000, 'E-commerce Packages', 100, 175, '24x24x24', 'available'),
('LD-2024-024', 'San Diego, CA', 'Sacramento, CA', '2024-12-21 08:00:00-08', '2024-12-22 08:00:00-08', 'Reefer', 1400.00, 'Wine shipment. Climate controlled.', 32000, 'Beverages', 60, 502, '48x40x48', 'available'),
('LD-2024-025', 'San Francisco, CA', 'Denver, CO', '2024-12-23 05:00:00-08', '2024-12-24 20:00:00-07', 'Dry Van', 2300.00, 'Tech equipment. Handle with care.', 26000, 'Electronics', 30, 1253, '48x40x48', 'available'),

-- LONG HAUL / CROSS COUNTRY
('LD-2024-026', 'Miami, FL', 'Seattle, WA', '2024-12-20 06:00:00-05', '2024-12-25 18:00:00-08', 'Dry Van', 5800.00, 'Cross country. Team drivers recommended.', 40000, 'Furniture', 15, 3304, '96x48x72', 'available'),
('LD-2024-027', 'Miami, FL', 'Los Angeles, CA', '2024-12-21 05:00:00-05', '2024-12-25 14:00:00-08', 'Reefer', 6200.00, 'Seafood. Temperature 32F. URGENT.', 34000, 'Frozen Seafood', 25, 2750, '48x40x48', 'available'),
('LD-2024-028', 'Boston, MA', 'San Francisco, CA', '2024-12-22 04:00:00-05', '2024-12-27 18:00:00-08', 'Dry Van', 7500.00, 'Premium rate. Expedited.', 35000, 'Medical Equipment', 10, 3095, '48x40x60', 'available'),

-- REGIONAL / SHORT HAUL
('LD-2024-029', 'Nashville, TN', 'Memphis, TN', '2024-12-19 11:00:00-06', '2024-12-19 16:00:00-06', 'Dry Van', 400.00, 'Local delivery. TWIC card required.', 20000, 'Music Equipment', 25, 212, '48x40x60', 'available'),
('LD-2024-030', 'Denver, CO', 'Salt Lake City, UT', '2024-12-20 07:00:00-07', '2024-12-20 18:00:00-07', 'Reefer', 950.00, 'Frozen goods. -10F required.', 35000, 'Frozen Foods', 30, 525, '48x40x48', 'available'),
('LD-2024-031', 'Phoenix, AZ', 'Albuquerque, NM', '2024-12-22 09:00:00-07', '2024-12-22 18:00:00-07', 'Dry Van', 750.00, 'Standard freight.', 28000, 'Retail Inventory', 40, 449, '48x40x40', 'available'),
('LD-2024-032', 'Oklahoma City, OK', 'Little Rock, AR', '2024-12-21 10:00:00-06', '2024-12-21 18:00:00-06', 'Dry Van', 550.00, 'Time sensitive.', 24000, 'Medical Supplies', 18, 338, '48x40x48', 'available'),

-- FLATBED SPECIALTY
('LD-2024-033', 'Houston, TX', 'Oklahoma City, OK', '2024-12-20 06:00:00-06', '2024-12-20 18:00:00-06', 'Flatbed', 1200.00, 'Pipe load. Straps provided.', 48000, 'Steel Pipes', 20, 441, '72x48x48', 'available'),
('LD-2024-034', 'Birmingham, AL', 'Nashville, TN', '2024-12-21 07:00:00-06', '2024-12-21 14:00:00-06', 'Flatbed', 600.00, 'Lumber. Tarps required.', 44000, 'Lumber', 50, 191, '96x48x36', 'available'),
('LD-2024-035', 'Pittsburgh, PA', 'Cleveland, OH', '2024-12-22 08:00:00-05', '2024-12-22 14:00:00-05', 'Flatbed', 450.00, 'Steel beams.', 50000, 'Steel Products', 6, 133, '144x48x48', 'available'),

-- REEFER SPECIALTY
('LD-2024-036', 'Fresno, CA', 'Dallas, TX', '2024-12-20 04:00:00-08', '2024-12-22 16:00:00-06', 'Reefer', 3400.00, 'Grapes. Temperature 34F.', 40000, 'Fresh Produce', 80, 1500, '48x40x48', 'available'),
('LD-2024-037', 'Tampa, FL', 'New York, NY', '2024-12-21 05:00:00-05', '2024-12-23 14:00:00-05', 'Reefer', 2900.00, 'Citrus fruits. Keep cool.', 38000, 'Fresh Produce', 60, 1137, '48x40x48', 'available'),

-- HIGH VALUE LOADS
('LD-2024-038', 'Memphis, TN', 'Los Angeles, CA', '2024-12-23 06:00:00-06', '2024-12-26 18:00:00-08', 'Dry Van', 4500.00, 'FedEx overflow. Priority.', 30000, 'Mixed Freight', 100, 1798, '48x40x48', 'available'),
('LD-2024-039', 'Louisville, KY', 'Miami, FL', '2024-12-22 05:00:00-05', '2024-12-24 16:00:00-05', 'Dry Van', 2200.00, 'Amazon packages. No delays.', 28000, 'E-commerce', 150, 893, '48x40x48', 'available'),
('LD-2024-040', 'Laredo, TX', 'Chicago, IL', '2024-12-21 06:00:00-06', '2024-12-23 20:00:00-06', 'Dry Van', 3200.00, 'Cross-border freight. Customs cleared.', 36000, 'Auto Parts', 40, 1466, '48x40x48', 'available');

-- No fake carriers - all carrier data comes from real FMCSA SAFER verification
