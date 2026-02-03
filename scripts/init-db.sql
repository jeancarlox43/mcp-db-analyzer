-- Script de inicialización de base de datos para desarrollo/testing
-- Este script crea tablas de ejemplo para probar el MCP server

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    full_name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de productos
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(100),
    stock_quantity INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de órdenes
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    shipping_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Tabla de items de órdenes
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL
);

-- Tabla de logs de actividad
CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar datos de ejemplo

-- Usuarios
INSERT INTO users (email, username, full_name, status) VALUES
    ('juan@example.com', 'juanperez', 'Juan Pérez', 'active'),
    ('maria@example.com', 'mariagomez', 'María Gómez', 'active'),
    ('carlos@example.com', 'carlosrod', 'Carlos Rodríguez', 'active'),
    ('ana@example.com', 'anamart', 'Ana Martínez', 'inactive'),
    ('luis@example.com', 'luisgarcia', 'Luis García', 'active'),
    ('sofia@example.com', 'sofialopez', 'Sofía López', 'active'),
    ('diego@example.com', 'diegosanchez', 'Diego Sánchez', 'pending'),
    ('laura@example.com', 'lauradiaz', 'Laura Díaz', 'active'),
    ('pedro@example.com', 'pedrotorres', 'Pedro Torres', 'active'),
    ('carmen@example.com', 'carmenruiz', 'Carmen Ruiz', 'active')
ON CONFLICT (email) DO NOTHING;

-- Productos
INSERT INTO products (name, description, price, category, stock_quantity) VALUES
    ('Laptop Pro 15', 'Laptop de alto rendimiento con 16GB RAM', 1299.99, 'Electrónica', 50),
    ('Mouse Inalámbrico', 'Mouse ergonómico con batería recargable', 29.99, 'Accesorios', 200),
    ('Teclado Mecánico RGB', 'Teclado gaming con switches Cherry MX', 149.99, 'Accesorios', 75),
    ('Monitor 27" 4K', 'Monitor IPS con HDR10', 449.99, 'Electrónica', 30),
    ('Auriculares Bluetooth', 'Cancelación de ruido activa', 199.99, 'Audio', 100),
    ('Webcam HD 1080p', 'Cámara con micrófono integrado', 79.99, 'Accesorios', 150),
    ('SSD 1TB NVMe', 'Almacenamiento de alta velocidad', 99.99, 'Almacenamiento', 80),
    ('Hub USB-C 7 en 1', 'Expansor de puertos multiuso', 49.99, 'Accesorios', 120),
    ('Silla Ergonómica', 'Silla de oficina con soporte lumbar', 349.99, 'Mobiliario', 25),
    ('Lámpara LED Escritorio', 'Luz regulable con carga inalámbrica', 59.99, 'Iluminación', 90)
ON CONFLICT DO NOTHING;

-- Órdenes
INSERT INTO orders (user_id, total_amount, status, shipping_address) VALUES
    (1, 1329.98, 'completed', 'Calle Principal 123, Ciudad'),
    (2, 279.97, 'completed', 'Av. Central 456, Ciudad'),
    (3, 449.99, 'shipped', 'Plaza Mayor 789, Ciudad'),
    (1, 149.99, 'processing', 'Calle Principal 123, Ciudad'),
    (4, 599.98, 'pending', 'Calle Norte 321, Ciudad'),
    (5, 1749.98, 'completed', 'Av. Sur 654, Ciudad'),
    (6, 89.98, 'completed', 'Calle Este 987, Ciudad'),
    (2, 349.99, 'shipped', 'Av. Central 456, Ciudad'),
    (7, 199.99, 'pending', 'Plaza Central 111, Ciudad'),
    (3, 129.98, 'completed', 'Plaza Mayor 789, Ciudad')
ON CONFLICT DO NOTHING;

-- Items de órdenes
INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal) VALUES
    (1, 1, 1, 1299.99, 1299.99),
    (1, 2, 1, 29.99, 29.99),
    (2, 3, 1, 149.99, 149.99),
    (2, 2, 2, 29.99, 59.98),
    (2, 8, 1, 49.99, 49.99),
    (3, 4, 1, 449.99, 449.99),
    (4, 3, 1, 149.99, 149.99),
    (5, 5, 2, 199.99, 399.98),
    (5, 5, 1, 199.99, 199.99),
    (6, 1, 1, 1299.99, 1299.99),
    (6, 4, 1, 449.99, 449.99),
    (7, 2, 1, 29.99, 29.99),
    (7, 10, 1, 59.99, 59.99),
    (8, 9, 1, 349.99, 349.99),
    (9, 5, 1, 199.99, 199.99),
    (10, 6, 1, 79.99, 79.99),
    (10, 8, 1, 49.99, 49.99)
ON CONFLICT DO NOTHING;

-- Logs de actividad
INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES
    (1, 'login', '{"browser": "Chrome", "os": "Windows"}', '192.168.1.100'),
    (1, 'view_product', '{"product_id": 1}', '192.168.1.100'),
    (1, 'add_to_cart', '{"product_id": 1, "quantity": 1}', '192.168.1.100'),
    (1, 'checkout', '{"order_id": 1}', '192.168.1.100'),
    (2, 'login', '{"browser": "Firefox", "os": "MacOS"}', '192.168.1.101'),
    (2, 'search', '{"query": "teclado"}', '192.168.1.101'),
    (3, 'login', '{"browser": "Safari", "os": "iOS"}', '192.168.1.102'),
    (3, 'view_product', '{"product_id": 4}', '192.168.1.102'),
    (4, 'login', '{"browser": "Edge", "os": "Windows"}', '192.168.1.103'),
    (5, 'login', '{"browser": "Chrome", "os": "Linux"}', '192.168.1.104')
ON CONFLICT DO NOTHING;

-- Crear índices útiles
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_action ON activity_logs(action);

-- Vista útil para análisis
CREATE OR REPLACE VIEW order_summary AS
SELECT 
    o.id as order_id,
    u.username,
    u.email,
    o.total_amount,
    o.status,
    o.created_at,
    COUNT(oi.id) as item_count
FROM orders o
JOIN users u ON o.user_id = u.id
LEFT JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.id, u.username, u.email, o.total_amount, o.status, o.created_at;

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'Base de datos inicializada correctamente con datos de ejemplo';
END $$;
