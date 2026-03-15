def fix_quotes(input_path, output_path):
    print(f"Fixing quotes in {input_path}...")
    with open(input_path, 'r', errors='replace') as fin, open(output_path, 'w') as fout:
        for line in fin:
            line = line.replace('\x00', '')
            if '404: Not Found' in line:
                continue
            # Count double quotes
            if line.count('"') % 2 != 0:
                line = line.strip() + '"\n'
            fout.write(line)

if __name__ == "__main__":
    fix_quotes('/Users/jarnox/FOOD/recipes.csv', '/Users/jarnox/FOOD/recipes_cleaned.csv')
