import pandas as pd

def load_dataset(file_path):
    """
    Load a dataset from a CSV file.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded dataset.
    """
    try:
        df = pd.read_csv(file_path)
        print(f"✅ Dataset loaded successfully with {df.shape[0]} rows and {df.shape[1]} columns.")
        return df
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return None


def total_reviews(df):
    """
    Returns the total number of reviews in the dataset.

    Args:
        df (pd.DataFrame): The dataset.

    Returns:
        int: Total number of reviews.
    """
    return df.shape[0]


def count_missing_values(df):
    """
    Counts the number of missing values per column.

    Args:
        df (pd.DataFrame): The dataset.

    Returns:
        pd.Series: Missing values count per column.
    """
    return df.isnull().sum()


def count_duplicates(df):
    """
    Counts the number of duplicate rows in the dataset.

    Args:
        df (pd.DataFrame): The dataset.

    Returns:
        int: Number of duplicate rows.
    """
    return df.duplicated().sum()


def get_column_info(df):
    """
    Provides an overview of column names, data types, and unique value counts.

    Args:
        df (pd.DataFrame): The dataset.

    Returns:
        pd.DataFrame: Summary of column information.
    """
    column_info = pd.DataFrame({
        "Column Name": df.columns,
        "Data Type": df.dtypes.values,
        "Unique Values": [df[col].nunique() for col in df.columns],
        "Missing Values": df.isnull().sum().values
    })

    return column_info


def basic_statistics(df, numerical_only=True):
    """
    Provides basic statistics of numerical or all columns.

    Args:
        df (pd.DataFrame): The dataset.
        numerical_only (bool): Whether to include only numerical columns (default: True).

    Returns:
        pd.DataFrame: Summary statistics of the dataset.
    """
    return df.describe(include="all" if not numerical_only else None)


def preview_data(df, num_rows=5):
    """
    Prints the first few rows of the dataset.

    Args:
        df (pd.DataFrame): The dataset.
        num_rows (int): Number of rows to print (default: 5).
    """
    print(f"\n📋 First {num_rows} Rows of the Dataset:")
    print(df.head(num_rows))


if __name__ == "__main__":
    # Example usage (this runs only if the script is executed directly)
    file_path = "data/cleaned_review_datasets.csv"  # Change as needed
    df = load_dataset(file_path)

    if df is not None:
        print("\n📊 Dataset Exploration:")
        print(f"Total Reviews: {total_reviews(df)}")
        print(f"Missing Values:\n{count_missing_values(df)}")
        print(f"Duplicate Rows: {count_duplicates(df)}")

        print("\n📝 Column Overview:")
        print(get_column_info(df))

        print("\n📈 Basic Statistics:")
        print(basic_statistics(df))

        preview_data(df)  # Print first 5 rows

