import type { FC } from 'react';
import { Box, FormControl, InputLabel, Select, MenuItem, Typography, SelectChangeEvent } from '@mui/material';

interface Business {
  id: string;
  name: string;
  active?: boolean;
}

interface BusinessSelectorProps {
  onBusinessChange: (businessId: string) => void;
  businesses?: Business[];
  selectedBusiness?: string;
}

const BusinessSelector: FC<BusinessSelectorProps> = ({ 
  onBusinessChange,
  businesses = [],
  selectedBusiness = ''
}) => {
  const handleChange = (event: SelectChangeEvent<string>) => {
    onBusinessChange(event.target.value);
  };

  return (
    <Box>
      {businesses.length === 0 ? (
        <Typography>No businesses available</Typography>
      ) : (
        <FormControl fullWidth>
          <InputLabel>Select Business</InputLabel>
          <Select
            value={selectedBusiness}
            onChange={handleChange}
            label="Select Business"
          >
            {businesses.map((business: Business) => (
              <MenuItem key={business.id} value={business.id}>
                {business.name} {business.active === false && '(Inactive)'}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}
    </Box>
  );
};

export default BusinessSelector;
