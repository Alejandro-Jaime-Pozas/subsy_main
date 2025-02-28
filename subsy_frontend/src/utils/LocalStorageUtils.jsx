export const safeParse = (key) => {
    try {
      const item = localStorage.getItem(key);
      if (!item || item === "undefined") return null; // Handle missing or incorrectly stored values
			return JSON.parse(item); // Return parsed JSON if available, otherwise return null
    } catch (error) {
      console.error(`Error parsing localStorage item ${key}:`, error);
      return null; // Return null if parsing fails
    }
  };
