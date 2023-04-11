
class Scrubber:
    """
    A class to scrub and transform a dictionary of parsed statistics.

    Methods:
        fix_conditions(self)
            Splits the 'Condition' key in the `parsed_stats` dictionary at the colon and
            only keeps the first part of the string.

        fix_vin(self)
            Renames the key 'VIN (Vehicle Identification Number)' in the `parsed_stats`
            dictionary to simply 'VIN'.

        fix_options(self)
            Splits the 'Options' key in the `parsed_stats` dictionary at the comma and
            creates a list of strings.

        fix_power_options(self)
            Splits the 'Power Options' key in the `parsed_stats` dictionary at the comma
            and creates a list of strings.

        merge_options(self)
            Combines the lists created by `fix_options` and `fix_power_options` into a
            single list.

        scrub(self, parsed_stats)
            Applies the above methods in a specific order to a dictionary of parsed statistics,
            returning a tuple of the cleaned `parsed_stats` dictionary and a log of which
            methods were successfully executed.
    """

    def fix_conditions(self):
        """Splits the 'Condition' key in the `parsed_stats` dictionary at the colon and
        only keeps the first part of the string."""
        self.parsed_stats['Condition'] = self.parsed_stats['Condition'].split(':')[0]

    def fix_vin(self):
        """Renames the key 'VIN (Vehicle Identification Number)' in the `parsed_stats`
        dictionary to simply 'VIN'."""

        if 'VIN (Vehicle Identification Number)' in self.parsed_stats.keys():
            self.parsed_stats['VIN'] = self.parsed_stats.pop('VIN (Vehicle Identification Number)')

        elif 'VIN' not in self.parsed_stats.keys:
            raise Exception('No VIN found on listing')
        
        elif self.parsed_stats['VIN'] == None:
            raise Exception('No VIN found on listing')
        
        

    def fix_options(self):
        """Splits the 'Options' key in the `parsed_stats` dictionary at the comma and
        creates a list of strings."""
        self.parsed_stats['Options'] = self.parsed_stats.pop('Options').split(', ')

    def fix_power_options(self):
        """Splits the 'Power Options' key in the `parsed_stats` dictionary at the comma
        and creates a list of strings."""
        self.parsed_stats['Power Options'] = self.parsed_stats.pop('Power Options').split(', ')

    def merge_options(self):
        """Combines the lists created by `fix_options` and `fix_power_options` into a
        single list."""
        self.parsed_stats['Options'] = list(self.parsed_stats.pop('Options')) + list(self.parsed_stats.pop('Power Options'))

    def scrub(self, parsed_stats):
        """
        Applies the above methods in a specific order to a dictionary of parsed statistics,
        returning a tuple of the cleaned `parsed_stats` dictionary and a log of which
        methods were successfully executed.

        Parameters:
            parsed_stats (dict): A dictionary of parsed statistics to be cleaned.

        Returns:
            tuple: A tuple containing the cleaned `parsed_stats` dictionary and a log
            of which methods were successfully executed.
        """
        self.parsed_stats = parsed_stats

        standard_funcs = [
            self.fix_conditions, 
            self.fix_vin,
            self.fix_options,
            self.fix_power_options
        ]

        log = {}

        for func in standard_funcs:
            try:
                func()
                log[func.__name__] = True

            except Exception as e:
                log[func.__name__] = False
        
        if log['fix_power_options'] and log['fix_options']:
            self.merge_options()
            log['merge_options'] = True
        else:
            log['merge_options'] = False
        
        return self.parsed_stats, log