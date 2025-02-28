export const safeParse = (key) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null; // Return parsed JSON if available, otherwise return null
    } catch (error) {
      console.error(`Error parsing localStorage item ${key}:`, error);
      return null; // Return null if parsing fails
    }
  };
