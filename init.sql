CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    position VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10, 2) NOT NULL,
    hire_date DATE NOT NULL DEFAULT CURRENT_DATE
);

INSERT INTO employees (name, position, department, salary) VALUES
('Alice Johnson', 'Software Engineer', 'Engineering', 85000.00),
('Bob Smith', 'Product Manager', 'Product', 95000.00),
('Charlie Brown', 'Data Analyst', 'Data Science', 70000.00);