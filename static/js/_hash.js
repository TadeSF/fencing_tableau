import bcrypt from "bcrypt";

async function hashPassword(password) {
  const saltRounds = 10;
  try {
    const hash = await bcrypt.hash(password, saltRounds);
    return hash;
  } catch (err) {
    throw err;
  }
}

export default hashPassword;