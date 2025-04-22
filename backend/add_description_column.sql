-- Add description column to businesses table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'businesses' 
        AND column_name = 'description'
    ) THEN
        ALTER TABLE businesses ADD COLUMN description VARCHAR(1000);
    END IF;
END $$;
