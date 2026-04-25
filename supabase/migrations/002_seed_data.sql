-- Happy Robot - Seed Data
-- Sample loads for testing the inbound carrier sales system

INSERT INTO loads (load_id, origin, destination, pickup_datetime, delivery_datetime, equipment_type, loadboard_rate, notes, weight, commodity_type, num_of_pieces, miles, dimensions, status) VALUES

-- Texas to California routes
('LD-2024-001', 'Houston, TX', 'Los Angeles, CA', '2024-12-20 08:00:00-06', '2024-12-22 18:00:00-08', 'Dry Van', 3500.00, 'Dock to dock delivery. Driver assistance required for unloading.', 42000, 'Consumer Electronics', 24, 1547, '48x40x48', 'available'),

('LD-2024-002', 'Dallas, TX', 'San Francisco, CA', '2024-12-21 06:00:00-06', '2024-12-23 20:00:00-08', 'Reefer', 4200.00, 'Temperature controlled at 35°F. Produce shipment.', 38000, 'Fresh Produce', 40, 1734, '48x40x40', 'available'),

('LD-2024-003', 'Austin, TX', 'Phoenix, AZ', '2024-12-19 14:00:00-06', '2024-12-20 16:00:00-07', 'Flatbed', 1800.00, 'Construction materials. Tarps required.', 45000, 'Building Materials', 12, 872, '96x48x48', 'available'),

-- Midwest routes
('LD-2024-004', 'Chicago, IL', 'Denver, CO', '2024-12-20 05:00:00-06', '2024-12-21 18:00:00-07', 'Dry Van', 2200.00, 'Standard freight. No special requirements.', 35000, 'General Merchandise', 30, 1003, '48x40x48', 'available'),

('LD-2024-005', 'Detroit, MI', 'Atlanta, GA', '2024-12-22 07:00:00-05', '2024-12-23 20:00:00-05', 'Dry Van', 1900.00, 'Automotive parts. Handle with care.', 28000, 'Auto Parts', 48, 721, '40x36x36', 'available'),

('LD-2024-006', 'Minneapolis, MN', 'Kansas City, MO', '2024-12-19 10:00:00-06', '2024-12-19 22:00:00-06', 'Dry Van', 850.00, 'Same day delivery requested.', 22000, 'Packaged Foods', 20, 437, '48x40x40', 'available'),

-- East Coast routes
('LD-2024-007', 'New York, NY', 'Miami, FL', '2024-12-21 04:00:00-05', '2024-12-23 16:00:00-05', 'Reefer', 3100.00, 'Pharmaceutical shipment. Temperature logs required.', 18000, 'Pharmaceuticals', 16, 1280, '48x40x48', 'available'),

('LD-2024-008', 'Boston, MA', 'Philadelphia, PA', '2024-12-20 12:00:00-05', '2024-12-20 20:00:00-05', 'Dry Van', 650.00, 'Quick turnaround needed.', 25000, 'Retail Goods', 35, 304, '48x40x40', 'available'),

('LD-2024-009', 'Charlotte, NC', 'Washington, DC', '2024-12-22 06:00:00-05', '2024-12-22 18:00:00-05', 'Flatbed', 1100.00, 'Steel coils. Chains and straps required.', 48000, 'Steel Products', 8, 391, '72x48x36', 'available'),

-- West Coast routes
('LD-2024-010', 'Seattle, WA', 'Portland, OR', '2024-12-19 09:00:00-08', '2024-12-19 14:00:00-08', 'Dry Van', 450.00, 'Short haul. Multiple stops.', 15000, 'E-commerce Packages', 100, 175, '24x24x24', 'available'),

('LD-2024-011', 'Los Angeles, CA', 'Las Vegas, NV', '2024-12-20 16:00:00-08', '2024-12-20 23:00:00-08', 'Dry Van', 700.00, 'Evening delivery preferred.', 30000, 'Hotel Supplies', 45, 270, '48x40x48', 'available'),

('LD-2024-012', 'San Diego, CA', 'Sacramento, CA', '2024-12-21 08:00:00-08', '2024-12-22 08:00:00-08', 'Reefer', 1400.00, 'Wine shipment. Climate controlled.', 32000, 'Beverages', 60, 502, '48x40x48', 'available'),

-- Long haul routes
('LD-2024-013', 'Miami, FL', 'Seattle, WA', '2024-12-20 06:00:00-05', '2024-12-25 18:00:00-08', 'Dry Van', 5800.00, 'Cross country. Team drivers recommended.', 40000, 'Furniture', 15, 3304, '96x48x72', 'available'),

('LD-2024-014', 'New York, NY', 'Los Angeles, CA', '2024-12-22 04:00:00-05', '2024-12-26 20:00:00-08', 'Dry Van', 5500.00, 'High value freight. GPS tracking required.', 38000, 'Electronics', 20, 2791, '48x40x48', 'available'),

('LD-2024-015', 'Chicago, IL', 'Houston, TX', '2024-12-21 08:00:00-06', '2024-12-23 16:00:00-06', 'Flatbed', 2400.00, 'Machinery. Oversized permits may be needed.', 50000, 'Industrial Equipment', 4, 1092, '144x96x84', 'available'),

-- Regional routes
('LD-2024-016', 'Nashville, TN', 'Memphis, TN', '2024-12-19 11:00:00-06', '2024-12-19 16:00:00-06', 'Dry Van', 400.00, 'Local delivery. Driver must have TWIC card.', 20000, 'Music Equipment', 25, 212, '48x40x60', 'available'),

('LD-2024-017', 'Denver, CO', 'Salt Lake City, UT', '2024-12-20 07:00:00-07', '2024-12-20 18:00:00-07', 'Reefer', 950.00, 'Frozen goods. -10°F required.', 35000, 'Frozen Foods', 30, 525, '48x40x48', 'available'),

('LD-2024-018', 'Phoenix, AZ', 'Albuquerque, NM', '2024-12-22 09:00:00-07', '2024-12-22 18:00:00-07', 'Dry Van', 750.00, 'Standard freight.', 28000, 'Retail Inventory', 40, 449, '48x40x40', 'available'),

('LD-2024-019', 'Oklahoma City, OK', 'Little Rock, AR', '2024-12-21 10:00:00-06', '2024-12-21 18:00:00-06', 'Dry Van', 550.00, 'Time sensitive.', 24000, 'Medical Supplies', 18, 338, '48x40x48', 'available'),

('LD-2024-020', 'Indianapolis, IN', 'Columbus, OH', '2024-12-19 13:00:00-05', '2024-12-19 17:00:00-05', 'Dry Van', 350.00, 'Quick delivery.', 18000, 'Office Supplies', 50, 176, '36x36x36', 'available');

-- Add some sample carriers for testing
INSERT INTO carriers (mc_number, legal_name, dba_name, phone, email, dot_number, entity_type, operating_status, is_verified, is_eligible) VALUES
('MC-123456', 'Swift Transportation LLC', 'Swift Trucking', '+1-555-0100', 'dispatch@swifttrucking.example.com', 'DOT-789012', 'Carrier', 'AUTHORIZED', true, true),
('MC-234567', 'Reliable Freight Inc', 'Reliable Freight', '+1-555-0101', 'loads@reliablefreight.example.com', 'DOT-890123', 'Carrier', 'AUTHORIZED', true, true),
('MC-345678', 'Express Logistics Co', 'Express Logistics', '+1-555-0102', 'ops@expresslogistics.example.com', 'DOT-901234', 'Carrier', 'AUTHORIZED', true, true);
